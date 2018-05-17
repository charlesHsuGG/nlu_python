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

from flask import Blueprint, request,  json

from nlu_server.utils.data_router import RasaNLU
from nlu_server.utils.file_manager import RasaFileManeger

from rasa_nlu.model import Metadata
from rasa_nlu.utils.langconv import *
from rasa_nlu.utils import json_to_string, write_json_to_file
from rasa_nlu.training_data import Message
from rasa_nlu.tokenizers.jieba_tokenizer import JiebaTokenizer
from rasa_nlu.extractors.duckling_http_extractor import DucklingHTTPExtractor
from rasa_nlu.extractors.duckling_extractor import extract_value
from rasa_nlu.extractors.mitie_entity_extractor import MitieEntityExtractor

from nlu_server.model.model import Entity, Tagtext, Value, Model

logger = logging.getLogger(__name__)

class EntityWeb(object):

    def data_router(self,rasaNLU):
        entity_webhook = Blueprint('entity_webhook', __name__)
        config = rasaNLU.config
        feature_extractor = rasaNLU.feature_extractor
        wv_model = rasaNLU.wv_model

        @entity_webhook.route("/get_model", methods=['POST'])
        def get_model():
            payload = request.json
            project_name = payload.get("model_name", None)
            if project_name is "":
                project_name = "system"
            print('project_name: '+project_name)
            model_db = Model()
            models = model_db.query.filter_by(model_name = project_name).all()
            print("model:"+str(models))
            model_list=[]
            for model in models:
                json ={
                    "model_id":model.model_id,
                    "model_name":model.model_name,
                    "model_path":model.model_path
                }
                model_list.append(json)
            return str(model_list)

        @entity_webhook.route("/entity_type_list", methods=['POST'])
        def entity_type_list():
            payload = request.json
            bot_id = payload.get("bot_id", None)
            entity_db = Entity()
            system_entities = entity_db.filter_by(entity_type = 'system').all()
            user_define_entities = entity_db.filter_by(entity_type = 'user', bot_id = bot_id).all()
            system_entity_list=[]
            for system_entity in system_entities:
                json ={
                    "entity_id":system_entity.entity_id,
                    "entity_name":system_entity.entity_name,
                    "entity_type":system_entity.entity_type,
                    "entity_extractor":system_entity.entity_extractor
                }
                system_entity_list.append(json)
            user_define_entity_list=[]
            for user_define_entity in user_define_entities:
                json ={
                    "entity_id":system_entity.entity_id,
                    "entity_name":system_entity.entity_name,
                    "entity_type":system_entity.entity_type,
                    "entity_extractor":system_entity.entity_extractor
                }
                user_define_entity_list.append(json)
            entity_list={
                "system_entities":system_entity_list,
                "user_define_entities":user_define_entity_list
            }
            return json_to_string(entity_list)

        @entity_webhook.route("/entity_extractor", methods=['POST'])
        def entity_extractor():
            payload = request.json
            text = payload.get("message", None)
            model_dir = payload.get("model_dir", None)
            model_metadata = Metadata.load(model_dir)
            print(str(model_metadata))
            output_attributes = {"entities": []}
            message = Message(text, output_attributes, time=None)
            tokens = JiebaTokenizer().tokenize(text)
            extracted = []
            duckling = DucklingHTTPExtractor(config["duckling_http_url"],
                                     config["language"],
                                     config["locale"],
                                     config["duckling_dimensions"])
            matches = duckling._duckling_parse(text)
            relevant_matches = duckling._filter_irrelevant_matches(matches)
            value_list = []
            for match in relevant_matches:
                value = extract_value(match)
                if value not in value_list:
                    entity = {
                        "start": match["start"],
                        "end": match["end"],
                        "value": match["body"],
                        "data": value,
                        "additional_info": match["value"],
                        "entity": match["dim"]}
                    extracted.append(entity)
                    value_list.append(value)
            extracted = duckling.add_extractor_name(extracted)
            message.set("entities",
                    message.get("entities", []) + extracted)
            entity_extractor_file = os.path.join(model_dir+"/nlu", model_metadata.get("entity_extractor_mitie"))
            extractor = mitie.named_entity_extractor(entity_extractor_file)
            ents = MitieEntityExtractor(extractor).extract_entities(text, tokens, feature_extractor)
            extracted = MitieEntityExtractor(extractor).add_extractor_name(ents)
            message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
            entities_output = []
            value_list = []
            for entity in message.get("entities"):
                if entity["value"] not in value_list:
                    entity_output = {"tag":entity["entity"],
                    "extractor":entity.get("extractor"),
                    "color":"#1E90FF",
                    "string":entity["value"]}
                    entities_output.append(entity_output)
                    value_list.append(entity["value"])
            output = {"code":1, "text": text, "entities": entities_output}
            return (json_to_string(output))

        @entity_webhook.route("/entity_save", methods=['POST'])
        def entity_save():
            payload = request.json
            title = payload.get("title", None)
            text = payload.get("message", None)
            entities = payload.get("entities", list())
            entity_list = []
            for entity in entities:

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
            rasa_json = mannger.nlu_load().get("rasa_nlu_data")
            comment_examples = rasa_json.get("common_examples", list())
            comment_examples.append(new_common)
            print("comment_examples_add:"+str(comment_examples))
            entity_synonyms = rasa_json.get("entity_synonyms", None)
            new_json = {
                "rasa_nlu_data": {
                "common_examples": comment_examples,
                "entity_synonyms": []
                }
            }
            mannger.nlu_save(json_to_string(new_json))
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @entity_webhook.route("/entity_crf_train", methods=['POST'])
        def entity_crf_train():
            mannger =RasaFileManeger(config["data"])
            data = mannger.nlu_load()
            comment_examples = data['rasa_nlu_data'].get("common_examples", list())


            entity_list_crf = model_metadata.get("ner_crf")

            dims = []
            if entity_list_crf is not None:
                entity_list_crf_file = os.path.join(model_dir+"/nlu", entity_list_crf)
                if os.path.exists(entity_list_crf_file):
                    with io.open(entity_list_crf_file, encoding="utf-8") as f:
                        data = json.loads(f.read())
                    dimensions_crf = data.get("dimensions", list())

                    for dim in dimensions_crf:
                        dims.append(dim)

            sents, labels = [], []
            for example in training_data.entity_examples:
                text = example.get("text")
                tokens = JiebaTokenizer().tokenize(text)
                print([t.text for t in tokens])
                word, tag = [], []
                for ent in example.get("entities", []):
                    value = ent["value"]
                    if ent["entity"] not in dims:
                        dims.append(ent["entity"])
                    for token in tokens:
                        if value.find(token.text) >= 0:
                            word.append(token.text)
                            last_tag = tag[-1:]
                            if last_tag:
                                if last_tag[0].find("O") is 0:
                                    tag.append("B-"+ent["entity"])
                                else:
                                    tag.append("I-"+ent["entity"])
                            else:
                                tag.append("B-"+ent["entity"])
                        else:
                            word.append(token.text)
                            tag.append("O")
                    sents.append(word)
                    labels.append(tag)
            model = {}
            for word in embedding.vocab:
                wv = embedding.word_vec(word)
                vector = np.array(wv)
                model[word] = vector
            x_train = np.asarray(sents)
            y_train = np.asarray(labels)
            print(len(x_train), 'train sequences')
            model = anago.Sequence(batch_size=1, word_emb_size=150,embeddings=wv_model)
            model.train(x_train, y_train, x_train, y_train)
            model.eval(x_train, y_train)
            entity_extractor_file = os.path.join(model_dir+"/nlu", "crf_entity_extractor")
            if not os.path.exists(entity_extractor_file):
                os.makedirs(entity_extractor_file)
            self.ner.save(entity_extractor_file)  
            file_name = "ner_crf.json"
            full_name = os.path.join(model_dir+"/nlu", file_name)
            write_json_to_file(full_name, {"dimensions": dims}) 
            response = {"code":1, "seccess": True}
            return (json_to_string(response))

        @entity_webhook.route("/entity_mitie_train", methods=['POST'])
        def entity_mitie_train():
            mannger =RasaFileManeger(config["data"])
            data = mannger.nlu_load()
            comment_examples = data['rasa_nlu_data'].get("common_examples", list())
            
            # Mitie will fail to train if there is not a single entity tagged
            payload = request.json
            model_dir = payload.get("model_dir", None)
            model_metadata = Metadata.load(model_dir)

            entity_list_mitie = model_metadata.get("ner_mitie")

            dims = []
            if entity_list_mitie is not None:
                entity_list_mitie_file = os.path.join(model_dir+"/nlu", entity_list_mitie)
                if os.path.exists(entity_list_mitie_file):
                    with io.open(entity_list_mitie_file, encoding="utf-8") as f:
                        data = json.loads(f.read())
                    dimensions_mitie = data.get("dimensions", list())

                    for dim in dimensions_mitie:
                        dims.append(dim)
            
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
                        if entity["entity"] not in dims:
                            dims.append(entity["entity"])
                    except Exception as e:
                        logger.warning("Failed to add entity example '{}' of sentence '{}'. Reason: {}".format(
                            str(e), str(text), e))
                        continue
                    found_one_entity = True
                trainer.add(sample)
            entity_extractor_file = os.path.join(model_dir+"/nlu", "entity_extractor.dat")
            # mitie_ner = mitie.named_entity_extractor(entity_extractor_file)
            if found_one_entity:
                mitie_ner = trainer.train()
            mitie_ner.save_to_disk(entity_extractor_file, pure_model=True)   
            file_name = "ner_mitie.json"
            full_name = os.path.join(model_dir+"/nlu", file_name)
            write_json_to_file(full_name, {"dimensions": dims}) 
            response = {"code":1, "seccess": True}
            return (json_to_string(response))


        return entity_webhook