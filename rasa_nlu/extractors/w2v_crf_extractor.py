from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import range, str
import logging
import os

import typing
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Text

import numpy as np

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.extractors import EntityExtractor
from rasa_nlu.model import Metadata
from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData
from rasa_nlu.utils.langconv import *

logger = logging.getLogger(__name__)


class CRFEntityExtractor(EntityExtractor):
    name = "ner_crf"

    provides = ["entities"]

    requires = ["tokens"]

    def __init__(self, ner=None):
        self.ner = ner
        
    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["gensim","anago"]

    @staticmethod
    def load_data_and_labels(example, tokens):
        word, tag = [], []
        for ent in example.get("entities", []):
            value = ent["value"]
            for token in tokens:
                if value.find(token.text) >= 0:
                    word.append(token.text)
                    if tag[-1].find("O") is 0:
                        tag.append("B-"+ent["entity"])
                    else:
                        tag.append("I-"+ent["entity"])
                else:
                    word.append(token.text)
                    tag.append("O")
        return word, tag
        

    def train(self, training_data, config, **kwargs):
        import anago
        embedding = kwargs.get("embedding")
        print(embedding)
        sents, labels = [], []
        for example in training_data.entity_examples:
            tokens = example.get("tokens")
            word, tag = CRFEntityExtractor.load_data_and_labels(example, tokens)
            sents.append(word)
            labels.append(tag)
        print(str(sents))
        print(str(labels))
        sents_np = np.asarray(sents)
        labels_np = np.asarray(labels)
        model = anago.Sequence(embeddings=embedding)
        self.ner = model.train(sents, labels, sents_np, labels_np)

        
    def process(self, message, **kwargs):
        import anago
        message.get
        matches = self.ner.analyze(message.text)
        ents = matches.get("entities")
        entities = []
        for ent in ents:
            entity = {
                "start": ent["beginOffset"],
                "end": ent["endOffset"],
                "text": ent["body"],
                "value": ent["text"],
                "entity": ent["type"]
            }
            entities.append(entity)
        extracted = self.add_extractor_name(entities)
        message.set("entities", message.get("entities", []) + extracted, add_to_output=True)

        
    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        import anago
        # type: (Text, Metadata, Optional[Word2VecNLP], **Any) -> Word2VecNLP
        if model_dir and model_metadata.get("entity_extractor_crf"):
            crf_extractor_file = os.path.join(model_dir, model_metadata.get("entity_extractor_crf"))
            embedding = kwargs.get("embedding")
            print(embedding)
            model = anago.Sequence(embeddings=embedding).load(crf_extractor_file)
            return CRFEntityExtractor(model)
        else:
            return CRFEntityExtractor()

    def persist(self, model_dir):
        if self.ner:
            entity_extractor_file = os.path.join(model_dir, "crf_entity_extractor")
            self.ner.save(entity_extractor_file)
            return {"entity_extractor_crf": "crf_entity_extractor"}
        else:
            return {"entity_extractor_crf": None}
        
