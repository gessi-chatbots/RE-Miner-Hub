import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SentimentAnalysisService:
    def __init__(self):
        self.endpoint = 'http://gessi-sw.essi.upc.edu:8080/sentiment-analysis-api/api/emotion'
        self.headers = {'Authorization': os.getenv("AUTHORITATION_KEY"), 'Content-Type': 'application/json'}

    def get_emotions(self, model, text):
        try:
            response = requests.post(self.endpoint, params={'tool': model}, headers=self.headers, json={'text': text})

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("Error in sentiment analysis request")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None