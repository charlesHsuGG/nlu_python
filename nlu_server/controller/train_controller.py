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

import typing
from typing import Text
from typing import Tuple
from typing import Optional

from flask import Blueprint, request,  json

from rasa_nlu.model import Metadata
from rasa_nlu.model import Interpreter
from rasa_nlu.utils.langconv import *
from rasa_nlu.utils import json_to_string
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.converters import load_data
from rasa_nlu.training_data import TrainingData, Message
from rasa_nlu.model import Trainer

from nlu_server.shared import db
from nlu_server.utils.data_router import RasaNLU
from nlu_server.utils.generate_key import generate_key_generator
from nlu_server.model.model import Entity, Article, EntityValue, Model, Intent, Sentence, Slot, Prompt, Admin

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from rasa_nlu.persistor import Persistor
class TrainWebController(object):

    def data_router(self,system_config):
        train_webhook = Blueprint('train_webhook', __name__)

        @train_webhook.route("/train", methods=['POST'])
        def train():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            model_db = Model()
            model = model_db.query.filter_by(model_id = model_id, admin_id = admin_id).first()
            nodes = model.node
            pipeline = []
            for node in nodes:
                pipeline.append(node.module_name)
            print(str(pipeline))

            model_config = system_config

            model_config.override({"mitie_file":model.mitie_embeding_path,
            "embedding_model_path":model.w2v_embeding_path,
            "embedding_type":model.w2v_embeding_type,
            "pipeline":pipeline})

            print(str(model_config.as_dict()))

            article_db = Article()
            articles = article_db.query.filter_by(admin_id = admin_id).all()
            data_list =[]
            for article in articles:
                text = article.article_content
                entity_values = article.entity_value
                entities = []
                for entity_value in entity_values:
                    value = entity_value.entity_value
                    start = entity_value.value_start
                    end = entity_value.value_end
                    entity_id = entity_value.entity_id
                    ent_db = Entity()
                    ent = ent_db.query.filter_by(entity_id = entity_id).first()
                    entity = ent.entity_name
                    entity_json = {
                        "entity":entity,
                        "start":start,
                        "end":end,
                        "value":value
                    }
                    entities.append(entity_json)
                data = {
                    "text":text,
                    "entities":entities
                }
                data_list.append(data)
            intent_db = Intent()
            intents = intent_db.query.filter_by(admin_id = admin_id).all()
            for intent in intents:
                intent_name = intent.intent_name
                sentences = intent.sentence
                for sent in sentences:
                    text = sent.sentence
                    slots = intent.slot
                    entities = []
                    for slot in slots:
                        ent_db = Entity()
                        ent = ent_db.query.filter_by(entity_id = slot.entity_id).first()
                        entity_name = ent.entity_name
                        slot_name = slot.name
                        replace_str = "{" + slot_name + "}"
                        if text.find(replace_str) >= 0:
                            text = text.replace(replace_str, entity_name)
                            start = text.find(entity_name)
                            end = start + len(entity_name)
                            entity_json = {
                                    "entity":entity_name,
                                    "start":start,
                                    "end":end,
                                    "value":entity_name
                                }
                            entities.append(entity_json)
                            ent_value_db = EntityValue()
                            ent_values = ent_value_db.query.filter_by(entity_id = slot.entity_id).all()
                            for ent_value in ent_values:
                                entity_json = {
                                    "entity":entity_name,
                                    "start":start,
                                    "end":end,
                                    "value":ent_value.entity_value
                                }
                                entities.append(entity_json)
                        # else:
                        #     entity_json = {
                        #             "entity":entity_name,
                        #             "start":start,
                        #             "end":end,
                        #             "value":entity_name
                        #         }
                        #     entities.append(entity_json)
                    data = {
                        "text":text,
                        "intent":intent_name,
                        "entities":entities
                    }
                    data_list.append(data)

            nlu_data = {
                "rasa_nlu_data": {
                    "common_examples":data_list
                }
            }
            trainer = Trainer(model_config)
            persistor = create_persistor(model_config)
            commons = nlu_data['rasa_nlu_data'].get("common_examples", list())
            training_examples = []
            for e in commons:
                data = e.copy()
                if "text" in data:
                    del data["text"]
                training_examples.append(Message(e["text"], data))
            train_data = TrainingData(training_examples)
            interpreter = trainer.train(train_data)
            admin_id = model.admin_id
            admin_db = Admin()
            admin = admin_db.query.filter_by(admin_id = admin_id).first()
            persisted_path = trainer.persist(model_config['system_path'], persistor,
                                            admin.admin_name,
                                            admin.admin_name+'_model_'+model.model_id)
            model.path = model_config['system_path'] + "/" + \
                            admin.admin_name + "/" + \
                            admin.admin_name+'_model'+model.model_id
            db.session.commit()
            response = {"code":1, "seccess": True, "nlu_data": nlu_data}
            return (json_to_string(response))


        return train_webhook

def create_persistor(config):
    # type: (RasaNLUConfig) -> Optional[Persistor]
    """Create a remote persistor to store the model if configured."""

    if config.get("storage") is not None:
        from rasa_nlu.persistor import get_persistor
        return get_persistor(config)
    else:
        return None
        