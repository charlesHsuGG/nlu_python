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

from nlu_server.utils.data_router import RasaNLU
from nlu_server.model.model import Intent, Sentence, Slot, Prompt
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
            intent = payload.get("intent", None)
            slots = []
            if 'slots' in payload:
                slots = payload.get("slots", list())
            sentences = payload.get("sentences", list())
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
            intent_db.create_date = datetime.datetime.now()

            sentences_list = []
            ent_save = False
            for sentence in sentences:
                slot_list = []
                for slot in slots:
                    name = slotent.get("name")
                    slot_type = slot.get("slot_type")
                    slot_prompts = slot.get("prompt", list())
                    entity_id = slot.get("entity_id")
                    entity_name = slot.get("entity_name")
                    required = slot.get("required")
                    slot_db = Slot()
                    if sentence.find(name) >= 0:
                        slot_db.slot_id = generate_key_generator()
                        slot_db.name = name
                        slot_db.slot_type = slot_type
                        slot_db.entity_id = entity_id
                        slot_db.entity_name = entity_name
                        slot_db.required = required
                        slot_prompt_list = []
                        for slot_prompt in slot_prompts:
                            prompt_text = slot_prompt.get("prompt_text")
                            action_type = slot_prompt.get("action_type")
                            slot_prompt_db = Prompt()
                            slot_prompt_db.prompt_id = generate_key_generator()
                            slot_prompt_db.prompt_text = prompt_text
                            slot_prompt_db.prompt_type = "entity"
                            slot_prompt_db.action_type = action_type
                            slot_prompt_list.append(slot_prompt_db)
                        slot_db.prompt = slot_prompt_list
                        slot_list.append(slot_db)
                sentences_db = Sentence()
                sentences_db.sentence_id = generate_key_generator()
                sentences_db.sentence = sentence
                sentences_db.slot = slot_list
                sentences_list.append(sentences_db)

            intent_db.sentence = sentences_list
            
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
            intent = payload.get("intent", None)
            create_date = payload.get("create_date")
            slots = []
            if 'slots' in payload:
                slots = payload.get("slots", list())
            sentences = payload.get("sentences", list())
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
            try:
                intent_db = Intent()

                intent_db.intent_id = intent_id
                intent_db.intent_name = intent
                intent_db.admin_id = admin_id
                intent_db.create_date = create_date
                intent_db.update_date = datetime.datetime.now()

                sentences_list = []
                for sentence in sentences:
                    slot_list = []
                    sentence_id = None
                    if "sentence_id" in sentence:
                        sentence_id = sentence.get("sentence_id")
                    sentence_text = sentence
                    for slot in slots:
                        slot_id = None
                        if "slot_id" in slot:
                            slot_id = ent.get("slot_id")
                        name = ent.get("name")
                        slot_type = ent.get("slot_type")
                        entity_id = slot.get("entity_id")
                        entity_name = slot.get("entity_name")
                        required = slot.get("required")
                        slot_prompts = ent.get("prompt", list())
                        slot_db = Slot()
                        if sentence_text.find(name) >= 0:
                            if slot_id is not None or slot_id is not "":
                                slot_db.slot_id = slot_id
                            else:
                                slot_db.slot_id = generate_key_generator()
                            slot_db.name = name
                            slot_db.slot_type = slot_type
                            slot_prompt_list = []
                            for slot_prompt in slot_prompts:
                                prompt_id = None
                                if "prompt_id" in slot_prompt:
                                    prompt_id = slot_prompt.get("prompt_id")
                                prompt_text = slot_prompt.get("prompt_text")
                                action_type = slot_prompt.get("action_type")
                                slot_prompt_db = Prompt()
                                if prompt_id is not None or prompt_id is not "":
                                    slot_prompt_db.prompt_id = prompt_id
                                else:
                                    slot_prompt_db.prompt_id = generate_key_generator()
                                slot_prompt_db.prompt_text = prompt_text
                                slot_prompt_db.prompt_type = "entity"
                                slot_prompt_db.action_type = action_type
                                slot_prompt_db.append(slot_prompt_db)
                            slot_db.prompt = slot_prompt_list
                            slot_list.append(slot_db)
                    sentences_db = Sentence()
                    if sentence_id is not None or sentence_id is not "":
                        sentences_db.sentence_id = sentence_id
                    else:
                        sentences_db.sentence_id = generate_key_generator()
                    sentences_db.sentence = sentence_text
                    sentences_db.slot = slot_list
                    sentences_list.append(sentences_db)

                intent_db.sentence = sentences_list
                
                prompt_list = []
                if confirm_prompt is not None:
                    prompt_id = None
                    if "prompt_id" in confirm_prompt:
                        prompt_id = confirm_prompt.get("prompt_id")
                    confirm_prompt_text = confirm_prompt.get("prompt_text")
                    action_type = confirm_prompt.get("action_type")
                    confirm_prompt_db = Prompt()
                    if prompt_id is not None or prompt_id is not "":
                        confirm_prompt_db.prompt_id = prompt_id
                    else:
                        confirm_prompt_db.prompt_id = generate_key_generator()
                    confirm_prompt_db.prompt_text = confirm_prompt_text
                    confirm_prompt_db.prompt_type = "confirm"
                    confirm_prompt_db.action_type = action_type
                    prompt_list.append(confirm_prompt_db)
                if cancel_prompt is not None:
                    prompt_id = None
                    if "prompt_id" in cancel_prompt:
                        prompt_id = cancel_prompt.get("prompt_id")
                    confirm_prompt_text = cancel_prompt.get("prompt_text")
                    action_type = cancel_prompt.get("action_type")
                    cancel_prompt_db = Prompt()
                    if prompt_id is not None or prompt_id is not "":
                        cancel_prompt_db.prompt_id = prompt_id
                    else:
                        cancel_prompt_db.prompt_id = generate_key_generator()
                    cancel_prompt_db.prompt_text = confirm_prompt_text
                    cancel_prompt_db.prompt_type = "cancel"
                    cancel_prompt_db.action_type = action_type
                    prompt_list.append(cancel_prompt_db)
                for response_prompt in response_prompts:
                    prompt_id = None
                    if "prompt_id" in response_prompt:
                        prompt_id = response_prompt.get("prompt_id")
                    response_prompt_text = response_prompt.get("prompt_text")
                    action_type = response_prompt.get("action_type")
                    response_prompt_db = Prompt()
                    if prompt_id is not None or prompt_id is not "":
                        response_prompt_db.prompt_id = prompt_id
                    else:
                        response_prompt_db.prompt_id = generate_key_generator()
                    response_prompt_db.prompt_text = response_prompt_text
                    response_prompt_db.prompt_type = "response"
                    response_prompt_db.action_type = action_type
                    prompt_list.append(response_prompt_db)

                intent_db.prompt = prompt_list

                db.session.delete(intents)
                db.session.commit()

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
            intent_db = Intent()
            intent_bots = intent_db.query.filter_by(admin_id = admin_id).all()
            
            intent_list=[]
            for int_bot in intent_bots:
                intent_id = int_bot.intent_id
                intent = int_bot.intent_name
                intent={
                    "intent_id":intent_id,
                    "intent":intent
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
            sentences = intents.sentence
            prompts = intents.prompt
            
            sent_list=[]
            slot_list=[]
            for sent in sentences:
                sentence_id = sent.sentence_id
                sentence_text = sent.sentence
                slots = sent.slot
                for slo in slots:
                    slot_id = slo.slot_id
                    name = slo.name
                    slot_type = slo.slot_type
                    entity_id = slo.entity_id
                    entity_name = slo.entity_name
                    required = slo.required
                    prom_list = []
                    for prom in slo.prompt:
                        prompt_id = prom.prompt_id
                        prompt_text = prom.prompt_text
                        prompt_type = prom.prompt_type
                        action_type = prom.action_type
                        ent_prompt_json = {
                            "prompt_id":prompt_id,
                            "prompt_text":prompt_text,
                            "prompt_type":prompt_type,
                            "action_type":action_type
                        }
                        prom_list.append(ent_prompt_json)
                    slot_json={
                            "slot_id":slot_id,
                            "name":name,
                            "slot_type":slot_type,
                            "prompt":prom_list,
                            "required":required,
                            "entity_id":entity_id,
                            "entity_name":entity_name
                    }
                    slot_list.append(slot_json)
                sent_json={
                    "sentence_id":sentence_id,
                    "sentence":sentence_text,
                }
                sent_list.append(sent_json)

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
                "sentence":sent_list,
                "slots":slot_list,
                "response_prompt":response_prompts
            }
            if confirm_prompt is not None:
                output.update({"confirm_prompt":confirm_prompt})
            if cancel_prompt is not None:
                output.update({"cancel_prompt":cancel_prompt})
            return (json_to_string(output))

        @intent_webhook.route("/binding_admin_intent", methods=['POST'])
        def binding_node_intent():
            payload = request.json
            admin_id = payload.get("admin_id", None)
            intent_id = payload.get("intent_id", None)
            intent_db = Intent()
            intents = intent_db.query.filter_by(intent_id = intent_id).first()
            
            response = {}
            if intents is not None:
                intents.admin_id = admin_id
                db.session.commit()

                response = {"code":1, "seccess": True}
            else:
                response = {"code":-1, "seccess": False}

            return (json_to_string(response))

        return intent_webhook