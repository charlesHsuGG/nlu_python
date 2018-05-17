from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


from flask import json

class RasaFileManeger(object):

    def __init__(self, file_name):
        self.file_name = file_name
        # set when parsing examples from a given intent
        self.current_intent = None
        self.common_examples = []
        self.entity_synonyms = []

    def nlu_load(self):
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

    def nlu_save(self,data):
        output = open(self.file_name,'w',encoding='utf-8')
        output.write(data)
        output.close()