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

from nlu_server.model.model import Entity, Article, EntityValue, Model, Intent, Sentence, Slot, Prompt, Admin


logger = logging.getLogger(__name__)

class ChatWebController(object):

    def data_router(self,system_config):
        chat_webhook = Blueprint('chat_webhook', __name__)

        @chat_webhook.route("/chat", methods=['POST'])
        def chat():
            payload = request.json
            text = payload.get("message", None)
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)

            result = find_intent(system_config, admin_id, model_id, text)

            print(result)
            
            intent = result.get("intent", None)
            intent_name = None
            if intent is not None:
                intent_name = intent.get("name")

            entities = result.get("entities", list())

            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_name = intent_name, admin_id = admin_id).first()
            
            secure_random = random.SystemRandom()

            if intents is not None:
                slots = intents.slot
                prompts = intents.prompt

                bot_response = None

                slot_list = []
                for slot in slots:
                    required = slot.required
                    entity_id = slot.entity_id
                    entity_db = Entity()
                    entity = entity_db.query.filter_by(entity_id = entity_id).first()
                    slot_json ={
                        "name" : entity.entity_name
                    }
                    ent_db = Entity()
                    ent = ent_db.query.filter_by(entity_id = entity_id).first()
                    fill_slot = False
                    if required == True:
                        for find_ent in entities:
                            if find_ent.get("entity").find(ent.entity_name) == 0:
                                slot_json.update({"value":find_ent.get("value")})
                                fill_slot = True
                        if fill_slot is True:
                            slot_json.update({"required":required, "fill_slot":True})
                        else:
                            slot_json.update({"required":required, "fill_slot":False})
                    else:
                        for find_ent in entities:
                            if find_ent.get("entity").find(ent.entity_name) == 0:
                                slot_json.update({"value":find_ent.get("value")})
                        slot_json.update({"required":required, "fill_slot":True})

                    slot_list.append(slot_json)

                select_option = False
                for slot in slot_list:
                    required_slot = slot.get("required")
                    fill_slot = slot.get("fill_slot")
                    if required_slot == True and fill_slot == False:
                        select_option = True
                slections = []
                check_list = []
                if select_option == True:
                    intent_db = Intent()
                    intents = intent_db.query.all()
                    for intent in intents:
                        intent_slots = intent.slot
                        for slot in slot_list:
                            if fill_slot == True:
                                for intent_slot in intent_slots:
                                    intent = intent_slot.intent_name
                                    entity_id = intent_slot.entity_id
                                    sentences = intent_slot.sentence
                                    entity_db = Entity()
                                    entity = entity_db.query.filter_by(entity_id = entity_id).first()
                                    if entity.entity_name.find(slot.get("name")) >= 0:
                                        sentence_list =[]
                                        for sentence in sentences:
                                            sentence_text = sent.sentence
                                            sentence_list.append(sentence_text)
                                        if intent not in intent:
                                            slections.append(secure_random.choice(sentence_list).prompt_text)
                                            check_list.append(intent)
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
                if check_list:
                    bot_response += "或者您想問:\n"
                    for slection in slections:
                        bot_response += slection + "\n"
                reponse_josn ={
                    "intent":intent_name,
                    "intent_ranking" : result.get("intent_ranking"),
                    "entities" : result.get("entities"),
                    "bot_response" : bot_response,
                    "slots" : slot_list
                }
            else:
                random_unknow_messages = ["我不明白你的意思","很抱歉,我學得還不夠多,不能明白你的意思"]
                bot_response = secure_random.choice(random_unknow_messages)

                reponse_josn ={
                    "intent":intent_name,
                    "intent_ranking" : result.get("intent_ranking"),
                    "entities" : result.get("entities"),
                    "bot_response" : bot_response
                }
            
            print(str(reponse_josn))
            return json_to_string(reponse_josn)

        return chat_webhook

def find_intent(system_config, admin_id, model_id, message):
    model_db = Model()
    model = model_db.query.filter_by(admin_id = admin_id, model_id = model_id).first()
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
    result = interpreter.parse(message)

    return result