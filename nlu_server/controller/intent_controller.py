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

from nlu_server.shared import db
from nlu_server.utils.data_router import RasaNLU
from nlu_server.model.model import Intent, Sentence, Slot, Prompt, Entity
from nlu_server.utils.generate_key import generate_key_generator

from rasa_nlu.utils import json_to_string


logger = logging.getLogger(__name__)

class IntentWebController(object):

    def data_router(self,system_config):
        intent_webhook = Blueprint('intent_webhook', __name__)

        @intent_webhook.route("/intent_save", methods=['POST'])
        def intent_save():
            payload = request.json
            print(payload)
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            intent = payload.get("intent", None)
            slots = []
            if 'slot' in payload:
                slots = payload.get("slot", list())
            sentences = payload.get("sentence", list())
            confirm_prompt = None
            if 'confirm_prompt' in payload:
                confirm_prompt = payload.get("confirm_prompt", None)
            cancel_prompt = None
            if 'cancel_prompt' in payload:
                cancel_prompt = payload.get("cancel_prompt", None)
            response_prompts = []
            if 'response_prompt' in payload:
                response_prompts = payload.get("response_prompt", list())

            intent_db = Intent()
            intent_db.intent_id = generate_key_generator()
            intent_db.intent_name = intent
            intent_db.admin_id = admin_id
            intent_db.model_id = model_id
            intent_db.create_date = datetime.datetime.now()

            sentences_list = []
            for sentence in sentences:
                sentences_db = Sentence()
                sentences_db.sentence_id = generate_key_generator()
                sentences_db.sentence = sentence.get("sentence")
                sentences_list.append(sentences_db)
            slot_list = []
            for slot in slots:
                entity_value_list = slot.get("entity_value", list())
                for entity_value in entity_value_list:
                    value = entity_value.get("entity_value", None)
                    entity = slot.get("entity")
                    ent_db = Entity()
                    ent = ent_db.query.filter_by(entity_name = entity).first()
                    entity_id = ent.entity_id
                    slot_prompts = slot.get("prompt", list())
                    required = slot.get("required")
                    slot_db = Slot()
                    slot_db.slot_id = generate_key_generator()
                    slot_db.name = value
                    slot_db.entity_id = entity_id
                    slot_db.required = required
                    # slot_prompt_list = []
                    # for slot_prompt in slot_prompts:
                    #     prompt_text = slot_prompt.get("prompt_text")
                    #     action_type = slot_prompt.get("action_type")
                    #     slot_prompt_db = Prompt()
                    #     slot_prompt_db.prompt_id = generate_key_generator()
                    #     slot_prompt_db.prompt_text = prompt_text
                    #     slot_prompt_db.prompt_type = "entity"
                    #     slot_prompt_db.action_type = action_type
                    #     slot_prompt_list.append(slot_prompt_db)
                    # slot_db.prompt = slot_prompt_list
                    slot_list.append(slot_db)

            intent_db.sentence = sentences_list
            intent_db.slot = slot_list
            
            prompt_list = []
            if confirm_prompt is not None:
                confirm_prompt_text = confirm_prompt.get("prompt_text")
                action_type = confirm_prompt.get("action_type")
                confirm_prompt_db = Prompt()
                confirm_prompt_db.prompt_id = generate_key_generator()
                confirm_prompt_db.prompt_text = confirm_prompt_text
                confirm_prompt_db.prompt_type = "confirm"
                confirm_prompt_db.action_type = action_type
                prompt_list.append(confirm_prompt_db)
            if cancel_prompt is not None:
                confirm_prompt_text = cancel_prompt.get("prompt_text")
                action_type = cancel_prompt.get("action_type")
                cancel_prompt_db = Prompt()
                cancel_prompt_db.prompt_id = generate_key_generator()
                cancel_prompt_db.prompt_text = confirm_prompt_text
                cancel_prompt_db.prompt_type = "cancel"
                cancel_prompt_db.action_type = action_type
                prompt_list.append(cancel_prompt_db)
            for response_prompt in response_prompts:
                response_prompt_text = response_prompt.get("prompt_text")
                action_type = response_prompt.get("action_type")
                response_prompt_db = Prompt()
                response_prompt_db.prompt_id = generate_key_generator()
                response_prompt_db.prompt_text = response_prompt_text
                response_prompt_db.prompt_type = "response"
                response_prompt_db.action_type = action_type
                prompt_list.append(response_prompt_db)

            intent_db.prompt = prompt_list


            db.session.add(intent_db)
            db.session.commit()
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @intent_webhook.route("/intent_update", methods=['POST'])
        def intent_update():
            payload = request.json
            intent_id = payload.get("intent_id", None)
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            intent = payload.get("intent", None)
            create_date = payload.get("create_date")
            slots = []
            if 'slot' in payload:
                slots = payload.get("slot", list())
            sentences = payload.get("sentence", list())
            confirm_prompt = None
            if 'confirm_prompt' in payload:
                confirm_prompt = payload.get("confirm_prompt", None)
            cancel_prompt = None
            if 'cancel_prompt' in payload:
                cancel_prompt = payload.get("cancel_prompt", None)
            response_prompt = []
            if 'response_prompt' in payload:
                response_prompts = payload.get("response_prompt", list())

            intent_delete_db = Intent()
            intents = intent_delete_db.query.filter_by(intent_id = intent_id).first()
            db.session.delete(intents)
            db.session.commit()
            try:

                intent_db = Intent()
                intent_db.intent_id = generate_key_generator()
                intent_db.intent_name = intent
                intent_db.admin_id = admin_id
                intent_db.model_id = model_id
                intent_db.create_date = create_date
                intent_db.update_date = datetime.datetime.now()

                sentences_list = []
                for sentence in sentences:
                    sentences_db = Sentence()
                    sentences_db.sentence_id = generate_key_generator()
                    sentences_db.sentence = sentence.get("sentence")
                    sentences_list.append(sentences_db)
                slot_list = []
                for slot in slots:
                    entity_value_list = slot.get("entity_value", list())
                    for entity_value in entity_value_list:
                        value = entity_value.get("entity_value", None)
                        entity = slot.get("entity")
                        ent_db = Entity()
                        ent = ent_db.query.filter_by(entity_name = entity).first()
                        entity_id = ent.entity_id
                        slot_prompts = slot.get("prompt", list())
                        required = slot.get("required")
                        slot_db = Slot()
                        slot_db.slot_id = generate_key_generator()
                        slot_db.name = value
                        slot_db.entity_id = entity_id
                        slot_db.required = required
                        # slot_prompt_list = []
                        # for slot_prompt in slot_prompts:
                        #     prompt_text = slot_prompt.get("prompt_text")
                        #     action_type = slot_prompt.get("action_type")
                        #     slot_prompt_db = Prompt()
                        #     slot_prompt_db.prompt_id = generate_key_generator()
                        #     slot_prompt_db.prompt_text = prompt_text
                        #     slot_prompt_db.prompt_type = "entity"
                        #     slot_prompt_db.action_type = action_type
                        #     slot_prompt_list.append(slot_prompt_db)
                        # slot_db.prompt = slot_prompt_list
                        slot_list.append(slot_db)

                intent_db.sentence = sentences_list
                intent_db.slot = slot_list
                
                prompt_list = []
                if confirm_prompt is not None:
                    confirm_prompt_text = confirm_prompt.get("prompt_text")
                    action_type = confirm_prompt.get("action_type")
                    confirm_prompt_db = Prompt()
                    confirm_prompt_db.prompt_id = generate_key_generator()
                    confirm_prompt_db.prompt_text = confirm_prompt_text
                    confirm_prompt_db.prompt_type = "confirm"
                    confirm_prompt_db.action_type = action_type
                    prompt_list.append(confirm_prompt_db)
                if cancel_prompt is not None:
                    confirm_prompt_text = cancel_prompt.get("prompt_text")
                    action_type = cancel_prompt.get("action_type")
                    cancel_prompt_db = Prompt()
                    cancel_prompt_db.prompt_id = generate_key_generator()
                    cancel_prompt_db.prompt_text = confirm_prompt_text
                    cancel_prompt_db.prompt_type = "cancel"
                    cancel_prompt_db.action_type = action_type
                    prompt_list.append(cancel_prompt_db)
                for response_prompt in response_prompts:
                    response_prompt_text = response_prompt.get("prompt_text")
                    action_type = response_prompt.get("action_type")
                    response_prompt_db = Prompt()
                    response_prompt_db.prompt_id = generate_key_generator()
                    response_prompt_db.prompt_text = response_prompt_text
                    response_prompt_db.prompt_type = "response"
                    response_prompt_db.action_type = action_type
                    prompt_list.append(response_prompt_db)

                intent_db.prompt = prompt_list


                db.session.add(intent_db)
                db.session.commit()
                response = {"code":1, "seccess": True}
            except:
                print("error update")
                response = {"code":-1, "seccess": False}
                # db.session.add(intents)
                # db.session.commit()

            return (json_to_string(response))
            


        @intent_webhook.route("/intent_delete", methods=['POST'])
        def intent_delete():
            payload = request.json
            intent_id = payload.get("intent_id", None)
            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_id = intent_id).first()

            db.session.delete(intents)
            db.session.commit()
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @intent_webhook.route("/intent_list", methods=['POST'])
        def intent_list():
           
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = None
            if "model_id" in payload:
                model_id = payload.get("model_id", None)
            intent_db = Intent()
            if model_id is not None:
                intent_bots = intent_db.query.filter_by(admin_id = admin_id,model_id = model_id).all()
            else:
                intent_bots = intent_db.query.filter_by(admin_id = admin_id).all()

            intent_list=[]
            for int_bot in intent_bots:
                intent_id = int_bot.intent_id
                intent = int_bot.intent_name
                create_date = int_bot.create_date
                intent={
                    "intent_id": intent_id,
                    "intent": intent,
                    "create_date": create_date.strftime('%Y-%m-%d %H:%M')
                }
                intent_list.append(intent)
            output = {"intent_list":intent_list}
            return (json_to_string(output))

        @intent_webhook.route("/intent_get", methods=['POST'])
        def intent_get():
            payload = request.json
            intent_id = payload.get("intent_id", None)
            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_id = intent_id).first()

            intent_id = intents.intent_id
            intent = intents.intent_name
            admin_id = intents.admin_id
            model_id = intents.model_id
            slots = intents.slot
            sentences = intents.sentence
            prompts = intents.prompt
            create_date = intents.create_date
            
            sent_list=[]
            for sent in sentences:
                sentence_id = sent.sentence_id
                sentence_text = sent.sentence
                sent_json={
                    "sentence_id":sentence_id,
                    "sentence":sentence_text,
                }
                sent_list.append(sent_json)
            slot_list=[]
            for slo in slots:
                slot_id = slo.slot_id
                name = slo.name
                entity_id = slo.entity_id
                ent_db = Entity()
                ent = ent_db.query.filter_by(entity_id = entity_id).first()
                required = slo.required
                # prom_list = []
                # for prom in slo.prompt:
                #     prompt_id = prom.prompt_id
                #     prompt_text = prom.prompt_text
                #     prompt_type = prom.prompt_type
                #     action_type = prom.action_type
                #     ent_prompt_json = {
                #             "prompt_id":prompt_id,
                #             "prompt_text":prompt_text,
                #             "prompt_type":prompt_type,
                #             "action_type":action_type
                #         }
                #     prom_list.append(ent_prompt_json)
                slot_json={
                        "slot_id":slot_id,
                        "entity":ent.entity_name,
                        "entity_value":[{
                            "entity_value":name,
                        }],
                        # "prompt":prom_list,
                        "required":required
                }
                slot_list.append(slot_json)
                

            confirm_prompt=None
            cancel_prompt=None
            response_prompts=[]
            for prompt in prompts:
                prompt_id = prompt.prompt_id
                prompt_text = prompt.prompt_text
                prompt_type = prompt.prompt_type
                action_type = prompt.action_type
                prompt_json = {
                    "prompt_id":prompt_id,
                    "prompt_text":prompt_text,
                    "prompt_type":prompt_type,
                    "action_type":action_type
                }
                if prompt_type.find("confirm") >= 0:
                    confirm_prompt = prompt_json
                if prompt_type.find("cancel") >= 0:
                    cancel_prompt = prompt_json
                if prompt_type.find("response") >= 0:
                    response_prompts.append(prompt_json)
            output={
                "intent_id":intent_id,
                "intent":intent,
                "admin_id":admin_id,
                "model_id":model_id,
                "sentence":sent_list,
                "slots":slot_list,
                "response_prompt":response_prompts,
                "create_date": create_date.strftime('%Y-%m-%d %H:%M')
            }
            if confirm_prompt is not None:
                output.update({"confirm_prompt":confirm_prompt})
            else:
                output.update({"confirm_prompt":"null"})
            if cancel_prompt is not None:
                output.update({"cancel_prompt":cancel_prompt})
            else:
                output.update({"cancel_prompt":"null"})
            return (json_to_string(output))

        @intent_webhook.route("/binding_admin_intent", methods=['POST'])
        def binding_node_intent():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            model_id = payload.get("model_id", None)
            intent_id = payload.get("intent_id", None)
            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_id = intent_id).first()
            
            response = {}
            if intents is not None:
                intents.admin_id = admin_id
                intents.model_id = model_id
                db.session.commit()

                response = {"code":1, "seccess": True}
            else:
                response = {"code":-1, "seccess": False}

            return (json_to_string(response))

        return intent_webhook