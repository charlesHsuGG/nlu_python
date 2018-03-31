"""This is a somewhat delicate package. It contains all registered components
and preconfigured templates.

Hence, it imports all of the components. To avoid cycles, no component should
import this in module scope."""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import typing
from rasa_nlu import utils
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Text
from typing import Type

from rasa_nlu.classifiers.keyword_intent_classifier import \
    KeywordIntentClassifier
from rasa_nlu.classifiers.sklearn_intent_classifier import \
    SklearnIntentClassifier
from rasa_nlu.classifiers.random_forest_classifier import \
    RandomForestClassifier
from rasa_nlu.extractors.duckling_extractor import DucklingExtractor
from rasa_nlu.extractors.duckling_http_extractor import DucklingHTTPExtractor
from rasa_nlu.extractors.entity_synonyms import EntitySynonymMapper
from rasa_nlu.extractors.w2v_crf_extractor import CRFEntityExtractor
from rasa_nlu.extractors.mitie_entity_extractor import MitieEntityExtractor
from rasa_nlu.featurizers.mitie_featurizer import MitieFeaturizer
from rasa_nlu.featurizers.regex_featurizer import RegexFeaturizer
from rasa_nlu.featurizers.wv_featurizer import EmbeddingFeaturizer
from rasa_nlu.model import Metadata
from rasa_nlu.tokenizers.jieba_tokenizer import JiebaTokenizer
from rasa_nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa_nlu.utils.mitie_utils import MitieNLP
from rasa_nlu.utils.wor2vec_utils import W2VNLP


if typing.TYPE_CHECKING:
    from rasa_nlu.components import Component
    from rasa_nlu.config import RasaNLUConfig

# Classes of all known components. If a new component should be added,
# its class name should be listed here.
component_classes = [
    MitieNLP, W2VNLP,
    CRFEntityExtractor, MitieEntityExtractor, DucklingExtractor,
    DucklingHTTPExtractor,
    EntitySynonymMapper,
    MitieFeaturizer, RegexFeaturizer, EmbeddingFeaturizer,
    WhitespaceTokenizer, JiebaTokenizer,
    SklearnIntentClassifier, KeywordIntentClassifier, RandomForestClassifier
]

# Mapping from a components name to its class to allow name based lookup.
registered_components = {c.name: c for c in component_classes}

# To simplify usage, there are a couple of model templates, that already add
# necessary components in the right order. They also implement
# the preexisting `backends`.
registered_pipeline_templates = {
    "mitie": [
        "nlp_mitie",
        "tokenizer_mitie",
        "ner_mitie",
        "ner_synonyms",
        "intent_entity_featurizer_regex",
        "intent_classifier_mitie",
    ],
    "mitie_sklearn": [
        "nlp_mitie",
        "tokenizer_mitie",
        "ner_mitie",
        "ner_synonyms",
        "intent_entity_featurizer_regex",
        "intent_featurizer_mitie",
        "intent_classifier_sklearn",
    ],
    "keyword": [
        "intent_classifier_keyword",
    ],
    # this template really is just for testing
    # every component should be in here so train-persist-load-use cycle can be
    # tested they still need to be in a useful order - hence we can not simply
    # generate this automatically.
    "all_components": [
        "nlp_mitie",
        "nlp_word2vec",
        "tokenizer_whitespace",
        "tokenizer_jieba",
        "intent_featurizer_mitie",
        "intent_featurizer_w2v",
        "intent_entity_featurizer_regex",
        "ner_mitie",
        "ner_crf",
        "ner_duckling",
        "ner_duckling_http",
        "ner_synonyms",
        "intent_classifier_keyword",
        "random_forest_classifier",
        "intent_classifier_sklearn",
    ]
}


def get_component_class(component_name):
    # type: (Text) -> Optional[Type[Component]]
    """Resolve component name to a registered components class."""

    if component_name not in registered_components:
        try:
            return utils.class_from_module_path(component_name)
        except Exception:
            raise Exception(
                    "Failed to find component class for '{}'. Unknown "
                    "component name. Check your configured pipeline and make "
                    "sure the mentioned component is not misspelled. If you "
                    "are creating your own component, make sure it is either "
                    "listed as part of the `component_classes` in "
                    "`rasa_nlu.registry.py` or is a proper name of a class "
                    "in a module.".format(component_name))
    return registered_components[component_name]


def load_component_by_name(component_name,  # type: Text
                           model_dir,  # type: Text
                           metadata,  # type: Metadata
                           cached_component,  # type: Optional[Component]
                           **kwargs  # type: **Any
                           ):
    # type: (...) -> Optional[Component]
    """Resolves a component and calls it's load method to init it based on a
    previously persisted model."""

    component_clz = get_component_class(component_name)
    return component_clz.load(model_dir, metadata, cached_component, **kwargs)


def create_component_by_name(component_name, config):
    # type: (Text, RasaNLUConfig) -> Optional[Component]
    """Resolves a component and calls it's create method to init it based on a
    previously persisted model."""

    component_clz = get_component_class(component_name)
    return component_clz.create(config)
