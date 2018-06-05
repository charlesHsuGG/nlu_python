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
import random


from rasa_nlu.utils import json_to_string
from rasa_nlu.model import Metadata
from rasa_nlu.model import Interpreter

from flask import Blueprint, request,  json

from nlu_server.model.model import Entity, Article, EntityValue, Config, Intent, Sentence, Slot, Prompt, Admin


logger = logging.getLogger(__name__)

class ChatWebController(object):

    def data_router(self,system_config):
        chat_webhook = Blueprint('chat_webhook', __name__)

        @chat_webhook.route("/chat", methods=['POST'])
        def chat():
            payload = request.json
            text = payload.get("message", None)
            admin_id = payload.get("admin_id", None)

            result = find_intent(system_config, admin_id, text)

            print(result)
            
            intent = result.get("intent", None)
            intent_name = intent.get("name")

            entities = result.get("entities", list())

            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_name = intent_name, admin_id = admin_id).first()

            slots = intents.slot
            prompts = intents.prompt

            bot_response = None
            secure_random = random.SystemRandom()

            slot_list = []
            for slot in slots:
                required = slot.required
                entity_id = slot.entity_id
                slot_name = slot.name
                slot_prompts = slot.prompt
                slot_json ={
                    slot_name : None
                }
                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_id = entity_id).first()
                if required is True:
                    required = False
                    for find_ent in entities:
                        if find_ent.get("entity").find(ent.entity_name) == 0:
                            slot_json[slot_name] = find_ent.get("value")
                            required = True
                    if required == False:
                        bot_response = secure_random.choice(slot_prompts).prompt_text

                else:
                    for find_ent in entities:
                        if find_ent.get("entity") is ent.entity_name:
                            slot_json[slot_name] = find_ent.get("value")
                slot_list.append(slot_json)

            if bot_response is None:
                respon_confirm = False
                confirm_prompts =[]
                response_prompts =[]
                for prompt in prompts:
                    if prompt.prompt_type.find("confirm") == 0 and prompt.prompt_text is not None:
                        confirm_prompts.append(prompt)
                        respon_confirm = True
                    if prompt.prompt_type.find("response") == 0 and prompt.prompt_text is not None:
                        response_prompts.append(prompt)
                print(str(confirm_prompts))
                print(str(response_prompts))
                if respon_confirm == True:
                    print(secure_random.choice(confirm_prompts))
                    bot_response = secure_random.choice(confirm_prompts).prompt_text
                else:
                    print(secure_random.choice(response_prompts))
                    bot_response = secure_random.choice(response_prompts).prompt_text

            reponse_josn ={
                "intent_ranking" : result.get("intent_ranking"),
                "entities" : result.get("entities"),
                "bot_response" : bot_response,
                "slots" : slot_list
            }
            
            print(str(reponse_josn))
            return json_to_string(reponse_josn)

        return chat_webhook

def find_intent(system_config, admin_id, message):
    config_db = Config()
    config = config_db.query.filter_by(admin_id = admin_id).first()
    nodes = config.node
    pipeline = []
    for node in nodes:
        pipeline.append(node.module_name)
    print(str(pipeline))
    model_metadata = Metadata.load(config.model_path)
    print(str(model_metadata.metadata))
    model_metadata.metadata.update({"mitie_file":config.mitie_embeding_path,
            "embedding_model_path":config.w2v_embeding_path,
            "embedding_type":config.w2v_embeding_type,
            "pipeline":pipeline})
    print(str(model_metadata.metadata))

    meta = Metadata(model_metadata.metadata, config.model_path)

    interpreter = Interpreter.create(meta, system_config)
    result = interpreter.parse(message)

    return result