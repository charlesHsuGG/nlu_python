from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

from rasa_nlu.data_router import DataRouter, InvalidProjectError, \
    AlreadyTrainingError

class RasaNLU(object):

    def __init__(self, config, feature_extractor, wv_model,  component_builder=None, testing=False):
        logging.basicConfig(filename=config['log_file'],
                            level=config['log_level'])
        logging.captureWarnings(True)
        logger.debug("Configuration: " + config.view())

        self.config = config
        self.feature_extractor = feature_extractor
        self.wv_model = wv_model
        self.data_router = self._create_data_router(config, component_builder)
        self._testing = testing

    def _create_data_router(self, config, component_builder):
        return DataRouter(config, component_builder)