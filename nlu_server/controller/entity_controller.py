from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import argparse
import logging
import os
import io
import re
import six
import glob
import mitie
import datetime

from flask import Blueprint, request,  json

from rasa_nlu.model import Metadata
from rasa_nlu.model import Interpreter
from rasa_nlu.utils.langconv import *
from rasa_nlu.utils import json_to_string

from nlu_server.shared import db
from nlu_server.utils.data_router import RasaNLU
from nlu_server.utils.generate_key import generate_key_generator
from nlu_server.model.model import Entity, Article, EntityValue, Model, Admin

logger = logging.getLogger(__name__)

class EntityWebController(object):

    def data_router(self,system_config):
        entity_webhook = Blueprint('entity_webhook', __name__)

        @entity_webhook.route("/entity_extractor", methods=['POST'])
        def entity_extractor():
            payload = request.json
            text = payload.get("message", None)
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)

            model_db = Model()
            model = model_db.query.filter_by(model_id = model_id, admin_id = admin_id).first()
            nodes = model.node
            pipeline = []
            for node in nodes:
                pipeline.append(node.module_name)
            print(str(pipeline))
            model_metadata = Metadata.load(model.model_path)
            print(str(model_metadata.metadata))
            model_metadata.metadata.update({"mitie_file":model.mitie_embeding_path,
            "embedding_model_path":model.w2v_embeding_path,
            "embedding_type":model.w2v_embeding_type,
            "pipeline":pipeline})
            print(str(model_metadata.metadata))

            meta = Metadata(model_metadata.metadata, model.model_path)

            interpreter = Interpreter.create(meta, system_config)
            result = interpreter.parse(text)
            print(str(result.get("entities")))
            response = {"code":1, "entities":result.get("entities")}
            return json_to_string(response)

        @entity_webhook.route("/article_save", methods=['POST'])
        def article_save():
            payload = request.json
            admin_id = payload.get("admin_id")
            model_id = payload.get("model_id")
            article_title = None
            if "article_title" in payload:
                article_title = payload.get("article_title", None)
            article_content = payload.get("article_content", None)
            entities = payload.get("entities", list())
            article_id = generate_key_generator()
            article_db = Article()
            article_db.article_id = article_id
            article_db.article_title = article_title
            article_db.article_content = article_content
            article_db.admin_id = admin_id
            article_db.model_id = model_id
            article_db.create_date = datetime.datetime.now()
            entity_value_list = []
            for entity in entities:
                entity_name = entity.get("entity")
                entity_extractor = None
                if "extractor" in entity:
                    entity_extractor = entity.get("extractor")
                if admin_id is "40w9dse0277455f634fw40439sd":
                    entity_type = "system"
                else:
                    entity_type = "user"
                value_from = entity.get("value_from")
                entity_value = entity.get("value")
                start = article_content.find(entity_value)
                end = start + len(entity_value)
                entity_value_db = EntityValue()
                entity_value_db.entity_value_id = generate_key_generator()
                entity_value_db.entity_value = entity_value
                entity_value_db.value_start = start
                entity_value_db.value_end = end
                entity_value_db.value_from = value_from
                entity_db = Entity()
                entity = entity_db.query.filter_by(entity_name = entity_name, entity_type = entity_type).first()
                if entity == None:
                    entity_id = generate_key_generator()
                    entity_db.entity_id = entity_id
                    entity_db.entity_name = entity_name
                    entity_db.entity_type = entity_type
                    entity_db.entity_extractor = entity_extractor
                    entity_db.admin_id = admin_id
                    db.session.add(entity_db)
                    entity_value_db.entity_id = entity_id
                else:
                    entity_id = entity.entity_id
                    entity_value_db.entity_id = entity_id
                entity_value_list.append(entity_value_db)
            article_db.entity_value = entity_value_list
            db.session.add(article_db)
            db.session.commit()
            
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @entity_webhook.route("/article_update", methods=['POST'])
        def article_update():
            payload = request.json
            admin_id = payload.get("admin_id")
            model_id = payload.get("model_id")
            article_id = payload.get("article_id")
            article_title = payload.get("article_title")
            article_content = payload.get("article_content")
            create_date = payload.get("create_date")
            entities = payload.get("entities", list())
            article_delete_db = Article()
            article = article_delete_db.query.filter_by(article_id = article_id).first()
            db.session.delete(article)
            db.session.commit()
            try:

                article_db = Article()
                article_db.article_id= generate_key_generator()
                article_db.article_title = article_title
                article_db.article_content = article_content
                article_db.admin_id = admin_id
                article_db.model_id = model_id
                article_db.create_date = create_date
                article_db.update_date = datetime.datetime.now()

                entity_value_list = []
                for entity in entities:
                    entity_name = entity.get("entity")
                    if admin_id is "40w9dse0277455f634fw40439sd":
                        entity_type = "system"
                    else:
                        entity_type = "user"
                    entity_extractor = None
                    if "extractor" in entity:
                        entity_extractor = entity.get("extractor")
                    value_from = entity.get("value_from")
                    entity_value_id = generate_key_generator()
                    entity_value = entity.get("value")
                    start = article_content.find(entity_value)
                    end = start + len(entity_value)
                    entity_value_db = EntityValue()
                    entity_value_db.entity_value_id = generate_key_generator()
                    entity_value_db.entity_value = entity_value
                    entity_value_db.value_start = start
                    entity_value_db.value_end = end
                    entity_value_db.value_from = value_from
                    entity_db = Entity()
                    entity = entity_db.query.filter_by(entity_name = entity_name, entity_type = entity_type).first()
                    if entity is not None:
                        entity_id = entity.entity_id
                        entity_value_db.entity_id = entity_id
                    else:
                        entity_id = generate_key_generator()
                        entity_db.entity_id = entity_id
                        entity_db.entity_name = entity_name
                        entity_db.entity_type = entity_type
                        entity_db.entity_extractor = entity_extractor
                        entity_db.admin_id = admin_id
                        db.session.add(entity_db)
                        db.session.commit()
                        entity_value_db.entity_id = entity_id
                    entity_value_list.append(entity_value_db)
                article_db.entity_value = entity_value_list

                db.session.add(article_db)
                db.session.commit()
                response = {"code":1, "seccess": True}
            except:
                print("error update")
                response = {"code":-1, "seccess": False}
            
            
            return (json_to_string(response))
        
        @entity_webhook.route("/article_delete", methods=['POST'])
        def article_delete():
            payload = request.json
            article_id = payload.get("article_id", None)
            article_delete_db = Article()
            article = article_delete_db.query.filter_by(article_id = article_id).first()

            db.session.delete(article)
            db.session.commit()
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @entity_webhook.route("/article_get", methods=['POST'])
        def article_get():
            payload = request.json
            article_id = payload.get("article_id", None)
            article_db = Article()
            article = article_db.query.filter_by(article_id = article_id).first()

            article_id = article.article_id
            article_title = article.article_title
            article_content = article.article_content
            entity_values = article.entity_value
            create_date = article.create_date
            admin_id = article.admin_id
            model_id = article.model_id

            entities = []
            for entity_value in entity_values:
                entity_value_id = entity_value.entity_value_id
                entity_value_name = entity_value.entity_value
                value_start = entity_value.value_start
                value_end = entity_value.value_end
                value_from = entity_value.value_from
                entity_id = entity_value.entity_id
                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_id = entity_id).first()
                entity_name = ent.entity_name
                entity_extractor = ent.entity_extractor
                entity_json = {
                    "entity":entity_name,
                    "value":entity_value_name,
                    "start":value_start,
                    "end":value_end,
                    "extractor":entity_extractor
                }
                entities.append(entity_json)
            
            response = {
                    "article_id":article_id,
                    "article_title":article_title,
                    "article_content":article_content,
                    "admin_id":admin_id,
                    "model_id":model_id,
                    "create_date":create_date.strftime('%Y-%m-%d %H:%M'),
                    "entities":entities
                }
            return (json_to_string(response))
        
        @entity_webhook.route("/article_list", methods=['POST'])
        def article_list():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            article_db = Article()
            articles = article_db.query.filter_by(admin_id = admin_id,model_id=model_id).all()
            article_list=[]
            for article in articles:
                json = {
                    "article_id":article.article_id,
                    "article_title":article.article_title,
                    "article_content":article.article_content,
                    "admin_id":article.admin_id,
                    "create_date":article.create_date.strftime('%Y-%m-%d %H:%M')
                }
                article_list.append(json)
            response = {"code":1, "seccess": True, "article_list":article_list}
            return (json_to_string(response))

        @entity_webhook.route("/entity_list", methods=['POST'])
        def entity_list():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            entity_db = Entity()
            system_entities = entity_db.query.filter_by(entity_type = 'system').all()
            user_define_entities = entity_db.query.filter_by(entity_type = 'user', admin_id = admin_id, model_id = model_id).all()
            ent_list=[]
            for system_entity in system_entities:
                json ={
                    "entity_id":system_entity.entity_id,
                    "entity_name":system_entity.entity_name,
                    "entity_type":system_entity.entity_type,
                    "entity_extractor":system_entity.entity_extractor
                }
                ent_list.append(json)
            for user_define_entity in user_define_entities:
                json ={
                    "entity_id":user_define_entity.entity_id,
                    "entity_name":user_define_entity.entity_name,
                    "entity_type":user_define_entity.entity_type,
                    "entity_extractor":user_define_entity.entity_extractor
                }
                ent_list.append(json)
            entity_list={
                "entities":ent_list
            }
            return json_to_string(entity_list)

        
        @entity_webhook.route("/entity_get", methods=['POST'])
        def entity_get():
            payload = request.json
            entity_id = payload.get("entity_id", None)
            entity_db = Entity()
            entity = entity_db.query.filter_by(entity_id = entity_id).first()
            entity_value_db = EntityValue()
            entity_values = entity_value_db.query.filter_by(entity_id = entity_id).all()
            synonyms_list = entity_value.synonyms.split(',')
            entity_value_list = []
            for entity_value in entity_values:
                json ={
                    "entity_value_id":entity_value.entity_value_id,
                    "entity_value":entity_value.entity_value,
                    "synonyms":synonyms_list,
                    "entity_id":entity_value.entity_id,
                    "value_from":entity_value.value_from
                }
                entity_value_list.append(json)

            entity_json ={
                    "entity_id":entity.entity_id,
                    "entity_name":entity.entity_name,
                    "entity_type":entity.entity_type,
                    "entity_extractor":entity.entity_extractor,
                    "entity_value_list":entity_value_list
            }
            return json_to_string(entity_json)

        @entity_webhook.route("/entity_save", methods=['POST'])
        def entity_save():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            entities = payload.get("entities", None)

            admin_db = Admin()
            admin = admin_db.query.filter_by(admin_id = admin_id).first()
            for entity in entities:
                entity_name = entity.get("entity", None)

                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_name = entity_name).first()

                if ent is None:
                    entity_db = Entity()
                    entity_id = generate_key_generator()
                    entity_db.entity_id = entity_id
                    entity_db.entity_name = entity_name
                    if admin.admin_name == "system":
                        entity_db.entity_type = "system"
                    else:
                        entity_db.entity_type = "user"
                    entity_db.admin_id = admin_id
                    entity_db.model_id = model_id

                    db.session.add(entity_db)
                    db.session.commit()
                    
                    entity_value_list = entity.get("entity_value_list", list())
                    
                    check_value = []
                    for entity_value in entity_value_list:
                        entity_value = entity_value.get("entity_value", None)
                        if entity_value not in check_value:
                            entity_value_db = EntityValue()
                            entity_value_db.entity_value_id = generate_key_generator()
                            entity_value_db.entity_value = entity_value
                            entity_value_db.value_from = "user"
                            entity_value_db.entity_id = entity_id
                            db.session.add(entity_value_db)
                            db.session.commit()
                            check_value.append(entity_value)
                else:

                    entity_value_list = entity.get("entity_value_list", list())

                    check_value = []
                    for entity_value in entity_value_list:
                        entity_value = entity_value.get("entity_value", None)
                        if entity_value not in check_value:
                            entity_value_db = EntityValue()
                            entity_value_db.entity_value_id = generate_key_generator()
                            entity_value_db.entity_value = entity_value
                            entity_value_db.value_from = "user"
                            entity_value_db.entity_id = ent.entity_id
                            db.session.add(entity_value_db)
                            db.session.commit()
                            check_value.append(entity_value)

            response = {"code":1, "seccess": True}
            return json_to_string(response)



        @entity_webhook.route("/entity_update", methods=['POST'])
        def entity_update():
            payload = request.json
            print(payload)
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            entities = payload.get("entities", None)

            admin_db = Admin()
            admin = admin_db.query.filter_by(admin_id = admin_id).first()
            for entity in entities:
                entity_name = entity.get("entity", None)

                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_name = entity_name).first()

                ent_value_db = EntityValue()
                entity_values = ent_value_db.query.filter_by(entity_id = ent.entity_id).all()

                for entity_value in entity_values:
                    db.session.delete(entity_value)
                    db.session.commit()
                
                entity_value_list = entity.get("entity_value_list", list())

                check_value = []
                for entity_value in entity_value_list:
                    entity_value = entity_value.get("entity_value", None)
                    if entity_value not in check_value:
                        entity_value_db = EntityValue()
                        entity_value_db.entity_value_id = generate_key_generator()
                        entity_value_db.entity_value = entity_value
                        entity_value_db.value_from = "user"
                        entity_value_db.entity_id = ent.entity_id
                        db.session.add(entity_value_db)
                        db.session.commit()
                        check_value.append(entity_value)

            response = {"code":1, "seccess": True}
            return json_to_string(response)

        @entity_webhook.route("/entity_delete", methods=['POST'])
        def entity_delete():
            payload = request.json
            print(payload)
            entity_id = payload.get("entity_id", None)

            ent_db = Entity()
            ent = ent_db.query.filter_by(entity_id = entity_id).first()

            ent_value_db = EntityValue()
            entity_value_list = ent_value_db.query.filter_by(entity_id = entity_id).all()

            for entity_value in entity_value_list:
                db.session.delete(entity_value)
                db.session.commit()
            
            db.session.delete(ent)
            db.session.commit()

            response = {"code":1, "seccess": True}
            return json_to_string(response)
        

        @entity_webhook.route("/entity_value_update", methods=['POST'])
        def entity_value_update():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            entities = payload.get("entities", None)
            print(entities)
            
            admin_db = Admin()
            admin = admin_db.query.filter_by(admin_id = admin_id).first()

            for entity in entities:
                entity_name = entity.get("entity", None)

                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_name = entity_name).first()
                
                entity_id = None
                if ent is None:
                    entity_db = Entity()
                    entity_id = generate_key_generator()
                    entity_db.entity_id = entity_id
                    entity_db.entity_name = entity_name
                    if admin.admin_name == "system":
                        entity_db.entity_type = "system"
                    else:
                        entity_db.entity_type = "user"
                    entity_db.admin_id = admin_id
                    entity_db.model_id = model_id

                    db.session.add(entity_db)
                    db.session.commit()
                else:
                    entity_id = ent.entity_id
                
                entity_value_list = entity.get("entity_value_list", list())

                for entity_value in entity_value_list:
                    value = entity_value.get("entity_value", None)
                    ent_value_db = EntityValue()
                    entity_value = ent_value_db.query.filter_by(entity_value = value, entity_id = entity_id).first()
                    print(entity_value)
                    if entity_value is None:
                        entity_value_db = EntityValue()
                        entity_value_db.entity_value_id = generate_key_generator()
                        entity_value_db.entity_value = value
                        entity_value_db.value_from = "user"
                        entity_value_db.entity_id = entity_id
                        db.session.add(entity_value_db)
                        db.session.commit()

            response = {"code":1, "seccess": True}
            return json_to_string(response)


        return entity_webhook