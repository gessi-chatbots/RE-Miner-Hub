import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SentimentAnalysisService:
    def __init__(self):
        self.endpoint = os.environ.get('SENTIMENT_ANALYSIS_API_URL', 'http://127.0.0.1:3005') + '/api/emotion'
        self.headers = {'Authorization': os.getenv("AUTHORIZATION_KEY"), 'Content-Type': 'application/json'}

    def get_emotions(self, model, text):
        try:
            response = requests.post(self.endpoint, params={'tool': model}, headers=self.headers, json={'text': text})

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 500:
                raise Exception("Error in sentiment analysis request")
            else:
                raise Exception("Error in sentiment analysis request")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None