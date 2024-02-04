import requests

class FeatureExtractionService:
    def __init__(self):
        self.extract_features_endpoint = 'http://127.0.0.1:5000/extract-features'

    def extract_features(self, text):
        try:
            nlp_response = requests.post(self.extract_features_endpoint, json={'text': text})

            if nlp_response.status_code == 200:
                return nlp_response.json()
            else:
                raise Exception("Error in NLP request")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
