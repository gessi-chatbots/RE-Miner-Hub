import os
import requests
from dotenv import load_dotenv

load_dotenv()

class APISentimentAnalysis:
    def __init__(self):
        self.endpoint = 'http://localhost:8080/api/emotion'
        self.headers = {'Authorization': os.getenv("AUTHORITATION_KEY"), 'Content-Type': 'application/json'}

    def get_emotions(self, model, text):
        try:
            response = requests.post(self.endpoint, params={'tool': model}, headers=self.headers, json={'text': text})
            #response = requests.post(self.endpoint+"?tool="+model, headers=self.headers, json={'text': text})
            print("response", response)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("Error in sentiment analysis request")
                #return "Error in sentiment analysis request", 500

        except Exception as e:
            print(f"An error occurred: {e}")
            return None