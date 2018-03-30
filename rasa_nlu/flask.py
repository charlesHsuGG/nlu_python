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
from functools import wraps

import simplejson
from builtins import str

from flask import Blueprint, Flask, request, render_template, json

from rasa_nlu.training_data import Message

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.data_router import DataRouter, InvalidProjectError, \
    AlreadyTrainingError
from rasa_nlu.train import TrainingException
from rasa_nlu.model import Metadata
from rasa_nlu.version import __version__
from rasa_nlu.utils import json_to_string
from rasa_nlu.utils.langconv import *
from rasa_nlu.tokenizers.jieba_tokenizer import JiebaTokenizer
from rasa_nlu.extractors.duckling_http_extractor import DucklingHTTPExtractor
from rasa_nlu.extractors.duckling_extractor import extract_value
from rasa_nlu.extractors.mitie_entity_extractor import MitieEntityExtractor

logger = logging.getLogger(__name__)

def create_argparser():
    parser = argparse.ArgumentParser(description='parse incoming text')
    parser.add_argument('-c', '--config',
                        help="config file, all the command line options can "
                             "also be passed via a (json-formatted) config "
                             "file. NB command line args take precedence")
    parser.add_argument('-ce', '--config_entity',
                        help="config file, for entity")
    parser.add_argument('-e', '--emulate',
                        choices=['wit', 'luis', 'dialogflow'],
                        help='which service to emulate (default: None i.e. use '
                             'simple built in format)')
    parser.add_argument('-l', '--language',
                        choices=['de', 'en'],
                        help="model and data language")
    parser.add_argument('-m', '--mitie_file',
                        help='file with mitie total_word_feature_extractor')
    parser.add_argument('-p', '--path',
                        help="path where project files will be saved")
    parser.add_argument('--pipeline',
                        help="The pipeline to use. Either a pipeline template "
                             "name or a list of components separated by comma")
    parser.add_argument('-P', '--port',
                        type=int,
                        help='port on which to run server')
    parser.add_argument('-t', '--token',
                        help="auth token. If set, reject requests which don't "
                             "provide this token as a query parameter")
    parser.add_argument('-w', '--write',
                        help='file where logs will be saved')

    return parser

class RasaNLU(object):

    app = Flask(__name__)

    def __init__(self, config, component_builder=None, testing=False):
        logging.basicConfig(filename=config['log_file'],
                            level=config['log_level'])
        logging.captureWarnings(True)
        logger.debug("Configuration: " + config.view())

        self.config = config
        self.data_router = self._create_data_router(config, component_builder)
        self._testing = testing

    def _create_data_router(self, config, component_builder):
        return DataRouter(config, component_builder)

class RasaFileManeger(object):

    def __init__(self, file_name):
        self.file_name = file_name
        # set when parsing examples from a given intent
        self.current_intent = None
        self.common_examples = []
        self.entity_synonyms = []
        self.load()

    def load(self):
        with open(self.file_name) as json_data:
            data = json.load(json_data)
        self.common_examples = data.get("rasa_nlu_data").get("common_examples")
        self.entity_synonyms = data.get("rasa_nlu_data").get("entity_synonyms")
        return {
            "rasa_nlu_data": {
                "common_examples": self.common_examples,
                "entity_synonyms": self.entity_synonyms
            }
        }

    def save(self,data):
        output = open(self.file_name,'w',encoding='utf-8')
        output.write(data)
        output.close()



class SimpleWeb(object):

    def data_router(self,rasaNLU):
        custom_webhook = Blueprint('custom_webhook', __name__)
        data_router = rasaNLU.data_router
        config = rasaNLU.config
        feature_extractor = mitie.total_word_feature_extractor(config["mitie_file"])

        @custom_webhook.route("/")
        def main():
            return render_template("MainPage.html")
        
        @custom_webhook.route("/parse", methods=['POST'])
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

        @custom_webhook.route("/project_list", methods=['GET'])
        def project_list():
            list_projects = [fn
                for fn in glob.glob(os.path.join(config['path']+"/default", '*'))
                if os.path.isdir(fn)]
            return str(list_projects)
        
        @custom_webhook.route("/entity_get", methods=['POST'])
        def entity_get():
            payload = request.json
            text = payload.get("message", None)
            model_dir = payload.get("model_dir", None)
            model_metadata = Metadata.load(model_dir)
            print(str(model_metadata))
            output_attributes = {"entities": []}
            message = Message(text, output_attributes, time=None)
            tokens = JiebaTokenizer().tokenize(text)
            # token_strs = [token.text for token in tokens]
            # message.set("tokens",token_strs)
            extracted = []
            duckling = DucklingHTTPExtractor(config["duckling_http_url"],
                                     config["language"],
                                     config["locale"],
                                     config["duckling_dimensions"])
            matches = duckling._duckling_parse(text)
            relevant_matches = duckling._filter_irrelevant_matches(matches)
            for match in relevant_matches:
                value = extract_value(match)
                entity = {
                    "start": match["start"],
                    "end": match["end"],
                    "value": match["body"],
                    "data": value,
                    "additional_info": match["value"],
                    "entity": match["dim"]}
                extracted.append(entity)
            extracted = duckling.add_extractor_name(extracted)
            message.set("entities",
                    message.get("entities", []) + extracted)
            entity_extractor_file = os.path.join(model_dir, model_metadata.get("entity_extractor_mitie"))
            extractor = mitie.named_entity_extractor(entity_extractor_file)
            ents = MitieEntityExtractor(extractor).extract_entities(text, tokens, feature_extractor)
            extracted = MitieEntityExtractor(extractor).add_extractor_name(ents)
            message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
            entities_output = []
            for entity in message.get("entities"):
                entity_output = {"tag":entity["entity"],
                "extractor":entity.get("extractor"),
                "color":"#1E90FF",
                "string":entity["value"]}
                entities_output.append(entity_output)
            output = {"code":1, "text": text, "entities": entities_output}
            return (json_to_string(output))

        @custom_webhook.route("/entity_save", methods=['POST'])
        def entity_save():
            payload = request.json
            text = payload.get("message", None)
            new_common_examples = payload.get("entities", list())
            entities = []
            for new_common_example in new_common_examples:
               if new_common_example.get("extractor").find("ner_mitie") >= 0:
                    entity = new_common_example.get("tag")
                    value = new_common_example.get("string")
                    start = text.find(value)
                    end = start + len(value)
                    entity_json = {
                        "start":start,
                        "end":end,
                        "entity":entity,
                        "value":value
                    }
                    print(entity_json)
                    entities.append(entity_json)
            new_common = {"text": text, "entities":entities}
            mannger =RasaFileManeger(config["data"])
            rasa_json = mannger.load().get("rasa_nlu_data")
            comment_examples = rasa_json.get("common_examples", list())
            comment_examples.append(new_common)
            print("comment_examples_add:"+str(comment_examples))
            entity_synonyms = rasa_json.get("entity_synonyms", None)
            new_json = {
                "rasa_nlu_data": {
                "common_examples": comment_examples,
                "entity_synonyms": entity_synonyms
                }
            }
            mannger.save(json_to_string(new_json))
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @custom_webhook.route("/entity_mitie_train", methods=['POST'])
        def entity_mitie_train():
            mannger =RasaFileManeger(config["data"])
            data = mannger.load()
            comment_examples = data['rasa_nlu_data'].get("common_examples", list())
            mitie_ner = None
            trainer = mitie.ner_trainer(config["mitie_file"])
            trainer.num_threads = config["num_threads"]
            found_one_entity = False
            for example in comment_examples:
                text = example.get("text")
                tokens = JiebaTokenizer().tokenize(text)
                print([t.text for t in tokens])
                sample = mitie.ner_training_instance([Converter('zh-hans').convert(t.text) for t in tokens])
                for entity in example.get("entities", list()):
                    try:
                        # if the token is not aligned an exception will be raised
                        start, end = MitieEntityExtractor.find_entity(entity, text, tokens)
                    except ValueError as e:
                        logger.warning("Example skipped: {}".format(str(e)))
                        continue
                    try:
                        # mitie will raise an exception on malicious input - e.g. on overlapping entities
                        sample.add_entity(list(range(start, end)), entity["entity"])
                    except Exception as e:
                        logger.warning("Failed to add entity example '{}' of sentence '{}'. Reason: {}".format(
                            str(e), str(text), e))
                        continue
                    found_one_entity = True
                trainer.add(sample)
            # Mitie will fail to train if there is not a single entity tagged
            payload = request.json
            model_dir = payload.get("model_dir", None)
            entity_extractor_file = os.path.join(model_dir, "entity_extractor.dat")
            # mitie_ner = mitie.named_entity_extractor(entity_extractor_file)
            if found_one_entity:
                mitie_ner = trainer.train()
            mitie_ner.save_to_disk(entity_extractor_file, pure_model=True)    
            response = {"code":1, "seccess": True}
            return (json_to_string(response))


        return custom_webhook

if __name__ == "__main__": 
    arg_parser = create_argparser()
    cmdline_args = {key: val
                    for key, val in list(vars(arg_parser.parse_args()).items())
                    if val is not None}
    rasa_nlu_config = RasaNLUConfig(
            cmdline_args.get("config"), os.environ, cmdline_args)
    rasa = RasaNLU(rasa_nlu_config)
    input_channel = SimpleWeb()
    rasa.app.register_blueprint(input_channel.data_router(rasa), url_prefix='/ai')
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('192.168.2.61', rasa_nlu_config['port']), rasa.app)
    http_server.serve_forever()