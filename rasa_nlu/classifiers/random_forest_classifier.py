from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import logging
import typing
from builtins import zip
import os
import io
from future.utils import PY3
from typing import Any, Optional
from typing import Dict
from typing import List
from typing import Text
from typing import Tuple

from rasa_nlu.components import Component
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Metadata
from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData

logger = logging.getLogger(__name__)

# How many intents are at max put into the output intent ranking, everything else will be cut off
INTENT_RANKING_LENGTH = 10

# We try to find a good number of cross folds to use during intent training, this specifies the max number of folds
MAX_CV_FOLDS = 5

if typing.TYPE_CHECKING:
    import sklearn
    import numpy as np


class RandomForestClassifier(Component):
    """Intent classifier using the sklearn framework"""

    name = "random_forest_classifier"

    provides = ["intent", "intent_ranking"]

    requires = ["text_features"]

    def __init__(self, clf=None, le=None):
        # type: (sklearn.model_selection.GridSearchCV, sklearn.preprocessing.LabelEncoder) -> None
        """Construct a new intent classifier using the sklearn framework."""
        from sklearn.preprocessing import LabelEncoder

        if le is not None:
            self.le = le
        else:
            self.le = LabelEncoder()
        self.clf = clf

    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["numpy", "sklearn"]

    def transform_labels_str2num(self, labels):
        # type: (List[Text]) -> np.ndarray
        """Transforms a list of strings into numeric label representation.

        :param labels: List of labels to convert to numeric representation"""

        return self.le.fit_transform(labels)

    def transform_labels_num2str(self, y):
        # type: (np.ndarray) -> np.ndarray
        """Transforms a list of strings into numeric label representation.

        :param y: List of labels to convert to numeric representation"""

        return self.le.inverse_transform(y)

    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, RasaNLUConfig, **Any) -> None
        """Train the intent classifier on a data set.

        :param num_threads: number of threads used during training time"""
        from sklearn.ensemble import RandomForestClassifier
        labels = [e.get("intent") for e in training_data.intent_examples]
        if len(set(labels)) < 2:
            logger.warning("Can not train an classifier. Need at least 2 different classes. " +
                           "Skipping training of classifier.")
        else:
            y = self.transform_labels_str2num(labels)
            # TODO fix it, in future sentence will replaced by "features"
            X = np.stack([example.get("text_features") for example in training_data.classify_examples])
            self.clf=RandomForestClassifier()
            self.clf.fit(X, y)

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None
        """Returns the most likely intent and its probability for the input text."""

        if not self.clf:
            # component is either not trained or didn't receive enough training data
            label = None
            label_ranking = []
        else:
            X = message.get("text_features").reshape(1, -1)
            label_ids, probabilities = self.predict(X)
            intents = self.transform_labels_num2str(label_ids)
            # `predict` returns a matrix as it is supposed
            # to work for multiple examples as well, hence we need to flatten
            intents, probabilities = intents.flatten(), probabilities.flatten()

            if intents.size > 0 and probabilities.size > 0:
                ranking = list(zip(list(intents), list(probabilities)))[:INTENT_RANKING_LENGTH]
                intent = {"name": intents[0], "confidence": probabilities[0]}
                intent_ranking = [{"name": intent_name, "confidence": score} for intent_name, score in ranking]
            else:
                intent = {"name": None, "confidence": 0.0}
                intent_ranking = []

        message.set("intent", intent, add_to_output=True)
        message.set("intent_ranking", intent_ranking, add_to_output=True)

    def predict_prob(self, X):
        # type: (np.ndarray) -> np.ndarray
        """Given a bow vector of an input text, predict the intent label. Returns probabilities for all labels.

        :param X: bow of input text
        :return: vector of probabilities containing one entry for each label"""

        return self.clf.predict_proba(X)

    def predict(self, X):
        # type: (np.ndarray) -> Tuple[np.ndarray, np.ndarray]
        """Given a bow vector of an input text, predict most probable label. Returns only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second, its probability"""

        import numpy as np

        pred_result = self.predict_prob(X)
        # sort the probabilities retrieving the indices of the elements in sorted order
        sorted_indices = np.fliplr(np.argsort(pred_result, axis=1))
        return sorted_indices, pred_result[:, sorted_indices]

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        # type: (Text, Metadata, Optional[Component], **Any) -> SklearnIntentClassifier
        import cloudpickle

        if model_dir and model_metadata.get("intent_classifier_ramdon_forest"):
            classifier_file = os.path.join(model_dir, model_metadata.get("intent_classifier_ramdon_forest"))
            with io.open(classifier_file, 'rb') as f:  # pragma: no test
                if PY3:
                    return cloudpickle.load(f, encoding="latin-1")
                else:
                    return cloudpickle.load(f)
        else:
            return RandomForestClassifier()

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]
        """Persist this model into the passed directory. Returns the metadata necessary to load the model again."""

        import cloudpickle

        classifier_file = os.path.join(model_dir, "ramdon_forest_intent_classifier.pkl")
        with io.open(classifier_file, 'wb') as f:
            cloudpickle.dump(self, f)

        return {
            "intent_classifier_ramdon_forest": "ramdon_forest_intent_classifier.pkl"
        }
