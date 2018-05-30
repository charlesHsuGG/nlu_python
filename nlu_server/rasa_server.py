from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

from multiprocessing import cpu_count, Process

import argparse
import logging
import os
import io
import re
import six
import glob
import mitie
import platform
import simplejson
from builtins import str
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, Flask, request, make_response,  json, jsonify

from rasa_nlu.config import RasaNLUConfig

from nlu_server.shared import db
from nlu_server.utils.data_router import RasaNLU
from nlu_server.controller.intent_controller import IntentWebController
from nlu_server.controller.entity_controller import EntityWebController
from nlu_server.controller.chat_controller import ChatWebController

logger = logging.getLogger(__name__)

app = Flask(__name__,static_folder='webapp/static')

class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/ai')

# Create database resources.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:54027890@192.168.2.71:3306/nlu_python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.route("/")
def index():
    return make_response(open('nlu_server/webapp/templates/MainPage.html').read())

db.init_app(app)

def serve_forever():
    http_server.start_accepting()
    http_server._stop_event.wait()

if __name__ == "__main__":
    system_name = platform.node()
    config_path = None
    try:
        filter_name = "nlu_server/resources/filter.json"
        with io.open(filter_name, encoding='utf-8') as f:
            filter_set = simplejson.loads(f.read())
            for setting in filter_set:
                name = setting.get("name")
                print(str(name))
                print(str(system_name))
                if system_name.find(name) == 0:
                    config_path = setting.get("path")
    except ValueError as e:
        raise InvalidConfigError("Failed to read configuration file '{}'. Error: {}".format(filter_name, e))
    print(str("nlu_server/resources"+config_path))
    config = {"config":"nlu_server/resources"+config_path}
    rasa_system_config = RasaNLUConfig(
            config.get("config"), os.environ, config)
    print(str(rasa_system_config.as_dict()))
    
    entity_channel = EntityWebController()
    intent_channel = IntentWebController()
    chat_channel = ChatWebController()
    app.register_blueprint(entity_channel.data_router(rasa_system_config), url_prefix='/ai_entity')
    app.register_blueprint(intent_channel.data_router(rasa_system_config), url_prefix='/ai_intent')
    app.register_blueprint(chat_channel.data_router(rasa_system_config), url_prefix='/chat')
    http_server = WSGIServer((rasa_system_config['server_ip'], rasa_system_config['port']), app)
    http_server.start()
    for i in range(cpu_count()):
        p = Process(target=serve_forever)
        p.start()