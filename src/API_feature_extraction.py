import requests

class APIFeatureExtraction:
    def __init__(self):
        self.endpoint = 'http://127.0.0.1:5000/extract-features'

    def extract_features(self, text):
        try:
            nlp_response = requests.post(self.endpoint, json={'text': text})

            if nlp_response.status_code == 200:
                return nlp_response.json()
            else:
                return "Error in NLP request", 500

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None