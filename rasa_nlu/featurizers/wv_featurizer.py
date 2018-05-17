from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import typing
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Text

from rasa_nlu.components import Component
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.featurizers import Featurizer
from rasa_nlu.tokenizers import Token
from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData

if typing.TYPE_CHECKING:
    import gensim
    import numpy as np
    from builtins import str


logger = logging.getLogger(__name__)

class EmbeddingFeaturizer(Featurizer):
    name = "intent_featurizer_w2v"

    provides = ["text_features"]

    requires = ["tokens"]

    def __init__(self, embedding=None):
        self.embeddings = embedding

    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["gensim", "numpy"]

    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, RasaNLUConfig, **Any) -> None
        import numpy as np
        embedding = kwargs.get("embedding")
        print(embedding)
        embedding_list = []
        for example in training_data.intent_examples:
            tokens = example.get("tokens")
            if tokens is not None:
                for token in tokens:
                    if token.text in embedding.vocab:
                        embedding_list.append(embedding.word_vec(token.text))
            if len(embedding_list) > 0:
                sentence_embeds = np.asarray(embedding_list, dtype=float).mean(axis=0)
                example.set("text_features", self._combine_with_existing_text_features(example, sentence_embeds))
            else:
                sentence_embeds = np.asarray(None, dtype=float).mean(axis=0)
                example.set("text_features", self._combine_with_existing_text_features(example, sentence_embeds))

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None
        import numpy as np
        embedding_list = []
        tokens = message.get("tokens")
        if tokens is not None:
            for token in tokens:
                if token.text in self.embeddings.vocab:
                    embedding_list.append(self.embeddings.word_vec(token.text, use_norm=True))
        if len(embedding_list) > 0:
            sentence_embeds = np.asarray(embedding_list, dtype=float).mean(axis=0)
            message.set("text_features", self._combine_with_existing_text_features(message, sentence_embeds))
        else:
            sentence_embeds = np.asarray(None, dtype=float).mean(axis=0)
            message.set("text_features", self._combine_with_existing_text_features(message, sentence_embeds))

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        # type: (Text, Metadata, Optional[Word2VecNLP], **Any) -> Word2VecNLP
        if cached_component:
            return cached_component
        embedding = kwargs.get("embedding")
        print(embedding)
        return EmbeddingFeaturizer(embedding)