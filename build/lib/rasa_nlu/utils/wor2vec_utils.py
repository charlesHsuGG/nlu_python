from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import typing
from builtins import str
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Text

from rasa_nlu.components import Component
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Metadata

if typing.TYPE_CHECKING:
    import gensim


class W2VNLP(Component):
    name = "nlp_word2vec"

    provides = ["embending_feature_extractor"]

    def __init__(self, embending_path, embedding_type, extractor=None):
        self.extractor = extractor
        self.embending_path = embending_path
        self.embending_type = embedding_type

    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["gensim"]

    @classmethod
    def create(cls, config):
        from gensim.models.keyedvectors import KeyedVectors
        embending_type = config["embedding_type"]
        is_binary = True if embending_type == "bin" else False
        return KeyedVectors.load_word2vec_format(config["embedding_path"], binary=is_binary)

    @classmethod
    def cache_key(cls, model_metadata):
        # type: (Metadata) -> Optional[Text]

        embedding_path = model_metadata.metadata.get("embedding_path", None)
        if embedding_path is not None:
            return cls.name + "-" + str(os.path.abspath(embedding_path))
        else:
            return None

    def provide_context(self):
        # type: () -> Dict[Text, Any]

        return {"word2vec_feature_extractor": self.extractor}

    @staticmethod
    def ensure_proper_language_model(extractor):
        # type: (Optional[mitie.total_word_feature_extractor]) -> None

        if extractor is None:
            raise Exception("Failed to load W2V feature extractor. Loading the model returned 'None'.")

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        # type: (Text, Metadata, Optional[MitieNLP], **Any) -> MitieNLP
        from gensim.models.keyedvectors import KeyedVectors

        if cached_component:
            return cached_component

        embending_type = model_metadata.get("embedding_type")
        is_binary = True if embending_type == "bin" else False
        embedding_path = model_metadata.get("embedding_path")
        return KeyedVectors.load_word2vec_format(embedding_path, binary=is_binary)

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]

        return {
            "embending_feature_extractor_fingerprint": self.extractor.fingerprint,
            "embedding_path": self.embending_path,
            "embedding_type": self.embending_type
        }
