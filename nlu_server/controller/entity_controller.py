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
from nlu_server.model.model import Entity, Article, EntityValue, Config

logger = logging.getLogger(__name__)

class EntityWebController(object):

    def data_router(self,system_config):
        entity_webhook = Blueprint('entity_webhook', __name__)

        @entity_webhook.route("/get_model", methods=['POST'])
        def get_model():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            print('admin_id: '+admin_id)
            config_db = Config()
            configs = config_db.query.filter_by(admin_id = admin_id).all()
            print("configs:"+str(configs))
            config_list=[]
            for config in configs:
                json ={
                    "config_id":config.config_id,
                    "config_name":config.config_name,
                    "model_path":config.model_path
                }
                config_list.append(json)
            return str(config_list)

        @entity_webhook.route("/entity_extractor", methods=['POST'])
        def entity_extractor():
            payload = request.json
            text = payload.get("message", None)
            config_id = payload.get("config_id", None)
            
            config_db = Config()
            config = config_db.query.filter_by(config_id = config_id).first()
            nodes = config.node
            pipline = []
            for node in nodes:
                pipline.append(node.module_name)
            print(str(pipline))
            model_metadata = Metadata.load(config.model_path)
            print(str(model_metadata.metadata))
            model_metadata.metadata.update({"mitie_file":config.mitie_embeding_path,
            "embedding_model_path":config.w2v_embeding_path,
            "embedding_type":config.w2v_embeding_type,
            "pipeline":pipline})
            print(str(model_metadata.metadata))

            meta = Metadata(model_metadata.metadata, config.model_path)

            interpreter = Interpreter.create(meta, system_config)
            result = interpreter.parse(text)
            print(str(result))
            return None

        @entity_webhook.route("/article_save", methods=['POST'])
        def article_save():
            payload = request.json
            article_title = payload.get("article_title", None)
            article_content = payload.get("article_content", None)
            entities = payload.get("entities", list())
            article_id = generate_key_generator()
            article_db = Article()
            article_db.article_id = article_id
            article_db.article_title = article_title
            article_db.article_content = article_content
            article_db.create_date = datetime.datetime.now()
            entity_value_list = []
            for entity in entities:
                entity_id = None
                if "entity_id" in entity:
                    entity_id = entity.get("entity_id")
                entity_name = entity.get("entity_name")
                entity_type = entity.get("entity_type")
                admin_id = entity.get("admin_id")
                entity_value = entity.get("entity_value")
                start = message.find(entity_value)
                end = start + len(entity_value)
                entity_value = EntityValue()
                entity_value.entity_value_id = generate_key_generator()
                entity_value.entity_value = entity_value
                entity_value.value_start = start
                entity_value.value_end = end
                entity_value.value_from = "article"
                entity_db = Entity()
                entity = entity_db.query.filter_by(entity_name = entity_name, entity_type = entity_type).first()
                if entity == None:
                    entity_id = generate_key_generator()
                    entity_db.entity_id = entity_id
                    entity_db.entity_name = entity_name
                    entity_db.entity_type = entity_type
                    db.session.add(intent_db)
                    entity_value.entity_id = entity_id
                else:
                    entity_id = entity.entity_id
                    entity_value.entity_id = entity_id
                entity_value_list.append(entity_value)
            article_db.entity_value = entity_value_list
            db.session.add(article_db)
            db.session.commit()
            
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @entity_webhook.route("/article_update", methods=['POST'])
        def article_update():
            payload = request.json
            article_id = payload.get("article_id")
            article_title = payload.get("article_title")
            article_content = payload.get("article_content")
            create_date = payload.get("create_date")
            entities = payload.get("entities", list())
            article_delete_db = Article()
            article = article_delete_db.query.filter_by(article_id = article_id).first()

            article_db = Article()
            article_db.article_id= article_id
            article_db.article_title = article_title
            article_db.article_content = article_content
            article_db.create_date = create_date
            article_db.update_date = datetime.datetime.now()

            entity_value_list = []
            for entity in entities:
                entity_id = None
                if "entity_id" in entity:
                    entity_id = entity.get("entity_id")
                entity_name = entity.get("entity_name")
                entity_type = entity.get("entity_type")
                admin_id = entity.get("admin_id")
                entity_value_id = None
                if "entity_value_id" in entity:
                    entity_value_id = entity.get("entity_value_id")
                entity_value = entity.get("entity_value")
                start = message.find(entity_value)
                end = start + len(entity_value)
                entity_value = EntityValue()
                if entity_value_id is not None or entity_value_id is not "":
                    entity_value.entity_value_id = entity_value_id
                else:
                    entity_value.entity_value_id = generate_key_generator()
                entity_value.entity_value = entity_value
                entity_value.value_start = start
                entity_value.value_end = end
                entity_value.value_from = "article"
                entity_db = Entity()
                entity = entity_db.query.filter_by(entity_name = entity_name, entity_type = entity_type).first()
                if entity == None:
                    entity_id = entity.entity_id
                    entity_value.entity_id = entity_id
                else:
                    entity_id = generate_key_generator()
                    entity_db.entity_id = entity_id
                    entity_db.entity_name = entity_name
                    entity_db.entity_type = entity_type
                    db.session.add(intent_db)
                    entity_value.entity_id = entity_id
                entity_value_list.append(entity_value)
            article_db.entity_value = entity_value_list

            db.session.delete(article)
            db.session.commit()

            db.session.add(article_db)
            db.session.commit()
            
            response = {"code":1, "seccess": True}
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
        
        @entity_webhook.route("/article_list", methods=['POST'])
        def article_list():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            article_db = Article()
            articles = article_db.query.filter_by(admin_id = admin_id).all()
            article_list=[]
            for article in articles:
                json = {
                    "article_id":article.article_id,
                    "article_title":article.article_title,
                    "article_content":article.article_content,
                    "admin_id":article.admin_id,
                    "create_date":article.create_date,
                    "update_date":article.update_date
                }
                article_list.append(json)
            response = {"code":1, "seccess": True, "article_list":article_list}
            return (json_to_string(response))

        @entity_webhook.route("/entity_list", methods=['POST'])
        def entity_list():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            entity_db = Entity()
            system_entities = entity_db.query.filter_by(entity_type = 'system').all()
            user_define_entities = entity_db.query.filter_by(entity_type = 'user', admin_id = admin_id).all()
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
            entity_value_list = []
            for entity_value in entity_values:
                json ={
                    "entity_value_id":entity_value.entity_value_id,
                    "entity_value":entity_value.entity_value,
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

        @entity_webhook.route("/entity_update", methods=['POST'])
        def entity_update():
            payload = request.json
            entity_id = payload.get("entity_id", None)
            entity_values = payload.get("entity_value_list", list())
            entity_value_db = EntityValue()
            entity = entity_value_db.query.filter_by(entity_id = entity_id).first()
            entity_value_list = []
            entity_value_list_db = []
            for entity_value in entity_values:
                entity_value_id = entity_value.get("entity_value_id")
                entity_value = entity_value.get("entity_value")
                entity_value_db = Value()
                entity_value = entity_value_db.query.filter_by(entity_value_id = entity_value_id).first()
                entity_value.entity_value = entity_value
                entity_value.value_start = start
                entity_value.value_end = start + len(entity_value)
                db.session.add(entity_value)
                db.session.commit()
                json ={
                    "entity_value_id":entity_value.entity_value_id,
                    "entity_value":entity_value.entity_value,
                    "entity_id":entity_value.entity_id,
                    "value_from":entity_value.value_from
                }
                value_list.append(json)

            entity_json ={
                    "entity_id":entity.entity_id,
                    "entity_name":entity.entity_name,
                    "entity_type":entity.entity_type,
                    "entity_extractor":entity.entity_extractor,
                    "entity_value_list":entity_value_list
            }
            return json_to_string(entity_json)


        return entity_webhook