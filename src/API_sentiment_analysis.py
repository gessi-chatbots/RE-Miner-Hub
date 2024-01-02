import requests

class APISentimentAnalysis:
    def __init__(self):
        self.endpoint = 'http://localhost:8080/api/emotion'
        self.headers = {'Authorization': 'ce3adcbe-1cdb-40f6-b107-8dd45ef246f4', 'Content-Type': 'application/json'}

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