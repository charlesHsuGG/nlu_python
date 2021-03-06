from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging
import os

import requests
import simplejson
from builtins import str
from typing import Any, Dict
from typing import List
from typing import Optional
from typing import Text

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.extractors import EntityExtractor
from rasa_nlu.model import Metadata
from rasa_nlu.training_data import Message
from rasa_nlu.extractors.duckling_extractor import extract_value
from rasa_nlu.utils import write_json_to_file

logger = logging.getLogger(__name__)


class DucklingHTTPExtractor(EntityExtractor):
    """Searches for structured entites, e.g. dates, using a duckling server."""

    name = "ner_duckling_http"

    provides = ["entities"]

    def __init__(self, duckling_url, language, locale):
        # type: (Text, Text, Optional[List[Text]]) -> None

        super(DucklingHTTPExtractor, self).__init__()
        self.duckling_url = duckling_url
        self.language = language
        self.locale = locale

    @classmethod
    def create(cls, config):
        # type: (RasaNLUConfig) -> DucklingHTTPExtractor

        return DucklingHTTPExtractor(config["duckling_http_url"],
                                     config["language"],
                                     config["locale"])

    def _duckling_parse(self, text):
        """Sends the request to the duckling server and parses the result."""

        try:
            # TODO: this is king of a quick fix to generate a proper locale
            #       for duckling. and might not always create correct
            #       locales. We should rather introduce a new config value.
            #locale = "{}_{}".format(self.language, self.language.upper())
            payload = {"text": text, "locale": self.locale, "lang": self.language}
            headers = {"Content-Type": "application/x-www-form-urlencoded; "
                                       "charset=UTF-8"}
            response = requests.post(self.duckling_url + "/parse",
                                     data=payload,
                                     headers=headers)
            if response.status_code == 200:
                return simplejson.loads(response.text)
            else:
                logger.error("Failed to get a proper response from remote "
                             "duckling. Status Code: {}. Response: {}"
                             "".format(response.status_code, response.text))
                return []
        except requests.exceptions.ConnectionError as e:
            logger.error("Failed to connect to duckling http server. Make sure "
                         "the duckling server is running and the proper host "
                         "and port are set in the configuration. More "
                         "information on how to run the server can be found on "
                         "github: "
                         "https://github.com/facebook/duckling#quickstart "
                         "Error: {}".format(e))
            return []

    # def _filter_irrelevant_matches(self, matches):
    #     """Only return dimensions the user configured"""

    #     if self.dimensions:
    #         return [match
    #                 for match in matches
    #                 if match["dim"] in self.dimensions]
    #     else:
    #         return matches

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None

        extracted = []
        if self.duckling_url is not None:

            matches = self._duckling_parse(message.text)
            # relevant_matches = self._filter_irrelevant_matches(matches)
            for match in matches:
                value = extract_value(match)
                entity = {
                    "start": match["start"],
                    "end": match["end"],
                    "text": match["body"],
                    "value": value,
                    "additional_info": match["value"],
                    "entity": match["dim"]}
                extracted.append(entity)
        else:
            logger.warn("Duckling HTTP component in pipeline, but no "
                        "`duckling_http_url` configuration in the config "
                        "file.")

        extracted = self.add_extractor_name(extracted)
        print("entities:"+str(extracted))
        message.set("entities",
                    message.get("entities", []) + extracted,
                    add_to_output=True)

    @classmethod
    def load(cls,
             model_dir=None,  # type: Text
             model_metadata=None,  # type: Metadata
             cached_component=None,  # type: Optional[DucklingHTTPExtractor]
             **kwargs  # type: **Any
             ):
        # type: (...) -> DucklingHTTPExtractor
        config = kwargs.get("config", {})
        
        return DucklingHTTPExtractor(config.get("duckling_http_url"),
                                     config.get("language"),
                                     config["locale"])
