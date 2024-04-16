import os
import logging
import requests
from exceptions.api_exceptions import TransfeatExException, RequestException
class FeatureService:
    def __init__ (self):
        self.transfeatex_endpoint = os.environ.get('TRANSFEATEX_URL', 'http://127.0.0.1:3004') + '/extract-features-aux'
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    def extract_features(self, text):
        try:
            logging.info(f"Sending text: {text} to Transfeatex {self.transfeatex_endpoint}")
            nlp_response = requests.post(self.transfeatex_endpoint, json={'text': text})
            if nlp_response.status_code == 200:
                logging.info(f"TransfeatEx response ok")
                return nlp_response.json()
            else:
                logging.error(f"Unnexpected status code response from Transfeatex {nlp_response.status_code}")
                raise TransfeatExException(f"Error: TransfeatEx response was {nlp_response.status_code}", 400)
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection error {e}")
            raise RequestException(f"There was an error on the request to TransfeatEx: {e}", 400)

        
    def format_features(text, ner_results):
        features = []
        current_feature = ""
        logging.info(f"Formatting features: {ner_results}")
        for feature in ner_results:
            start = feature['start']
            end = feature['end']

            # Hot fix to get the whole word
            blank_space = False
            while start > 0 and not blank_space and not text[start] == ' ':
                if text[start - 1] != ' ':
                    start -= 1
                else:
                    blank_space = True

            blank_space = False
            while end < len(text) - 1 and not blank_space and not text[end] == ' ':
                if text[end + 1] != ' ':
                    end += 1
                else:
                    blank_space = True

            f = text[start:end + 1]

            if feature['entity'] == 'B-feature':
                # If we were processing a feature, it is saved
                if len(current_feature) > 0:
                    features.append(current_feature.strip().lower())
                    current_feature = ""
                # current_feature += f + " "
                current_feature += f

            elif feature['entity'] == 'I-feature':
                # hot fix to make sure a feature does not have the same word twice
                if f not in current_feature:
                    current_feature += f + " "

            elif feature['entity'] == 'O':
                # If we were processing a feature, it is saved
                if len(current_feature) > 0:
                    features.append(current_feature.strip().lower())
                    current_feature = ""

        if len(current_feature) > 0:
            features.append(current_feature.strip().lower())
        return features
