from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
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

MAX_WORDS_IN_BATCH = 10000
logger = logging.getLogger(__name__)

class W2VNLP(Component):
    name = "nlp_word2vec"

    provides = ["embending_feature_extractor"]

    def __init__(self, config, model_metadata=None, wv_model=None):
        if config is None:
            self.embedding_model_path = model_metadata.get("embedding_model_path")
            from gensim.models.keyedvectors import KeyedVectors
            is_binary = True if model_metadata.get("embedding_type") == "bin" else False
            self.wv_model = KeyedVectors.load_word2vec_format(self.embedding_model_path, binary=is_binary)
        else:
            self.embedding_model_path = config["embedding_model_path"]
            self.embedding_type = config["embedding_type"]
            self.corpus = config["embedding_corpus_path"]
            self.wv_model = wv_model

    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["gensim"]

    @classmethod
    def create(cls, config):
        return W2VNLP(config)

    @classmethod
    def cache_key(cls, model_metadata):
        # type: (Metadata) -> Optional[Text]
        return None

    def provide_context(self):
        # type: () -> Dict[Text, Any]

        return {"embedding": self.wv_model}

    def train(self, training_data, config, **kwargs):
        # type: (Optional[mitie.total_word_feature_extractor]) -> None

        from gensim.models import Word2Vec
        import os.path


        if os.path.exists(self.embedding_model_path):
            # already have model
            if self.corpus:
                corpus = self.process_raw_data(self.corpus)
                from gensim.models.keyedvectors import KeyedVectors
                is_binary = True if self.embedding_type == "bin" else False
                self.wv_model = KeyedVectors.load_word2vec_format(self.embedding_model_path, binary=is_binary)
                self.wv_model.train(corpus, total_examples=self.wv_model.corpus_count, epochs=self.wv_model.iter)
                logger.info("retrain model") 
            else:
                from gensim.models.keyedvectors import KeyedVectors
                is_binary = True if self.embedding_type == "bin" else False
                self.wv_model = KeyedVectors.load_word2vec_format(self.embedding_model_path, binary=is_binary)
                logger.info("setting model as training data")
        else:
            if self.corpus:
                corpus = self.process_raw_data(self.corpus)
                model = Word2Vec(corpus, size=config.train_config["size"],
                             alpha=config.train_config["alpha"],
                             window=config.train_config["window"],
                             min_count=config.train_config["min_count"],
                             workers=config.train_config["workers"],
                             sample=config.train_config["sample"],
                             sg=config.train_config["sg"],
                             hs=config.train_config["hs"],
                             negative=config.train_config["negative"],
                             cbow_mean=1, iter=config.train_config["iter"])
                self.wv_model = model

            else:
                logger.error("need Data corpus file path.")

        
    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        # type: (Text, Metadata, Optional[MitieNLP], **Any) -> MitieNLP

        if cached_component:
            return cached_component

        return W2VNLP(None, model_metadata = model_metadata)

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]
        if os.path.exists(self.embedding_model_path):
            persist_config = {
                "embedding_model_path": self.embedding_model_path,
                "embedding_type": self.embedding_type
            }
        else:
            mkdir = './data/vectors.txt.word2vec'
            is_binary = True if self.embedding_type == "bin" else False
            self.wv_model.wv.save_word2vec_format(mkdir, binary=is_binary)
            persist_config = {
                "embedding_model_path": mkdir,
                "embedding_type": self.embedding_type
            }
        return persist_config

    @classmethod
    def process_raw_data(cls, sentences, max_sentence_length=MAX_WORDS_IN_BATCH, limit=None):
        from gensim.models.word2vec import LineSentence
        if sentences is not None:
            return LineSentence(sentences, max_sentence_length=max_sentence_length, limit=limit)
        raise ValueError("Sentences needs at least one sentence.")