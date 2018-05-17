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

from nlu_server.utils.data_router import RasaNLU

from rasa_core.agent import Agent
from rasa_core.channels.channel import UserMessage
from rasa_core.interpreter import RasaNLUInterpreter

from flask import Blueprint, request,  json

logger = logging.getLogger(__name__)

class ChatWeb(object):

    def data_router(self,rasaNLU):
        chat_webhook = Blueprint('chat_webhook', __name__)
        data_router = rasaNLU.data_router
        config = rasaNLU.config

        @chat_webhook.route("/chat", methods=['POST'])
        def chat():
            payload = request.json
            model_dir = payload.get("model_dir", None)
            sender_id = payload.get("sender", None)
            text = payload.get("message", None)
            interpreter = RasaNLUInterpreter(model_dir)
            agent = Agent.load(model_dir+"/dialogue", interpreter=interpreter)
            message = agent.handle_message(text)
            return jsonify(message)

        @chat_webhook.route("/parse", methods=['POST'])
        def parse_get():
            payload = request.json
            text = payload.get("message", None)
            print(text)
            request_params = {}
            request_params['q'] = text
            data = data_router.extract(request_params)
            print(data)
            try:
                response = data_router.parse(data)
                return (json_to_string(response))
            except InvalidProjectError as e:
                return (json_to_string({"error": "{}".format(e)}))
            except Exception as e:
                logger.exception(e)
                return (json_to_string({"error": "{}".format(e)}))

        return chat_webhook