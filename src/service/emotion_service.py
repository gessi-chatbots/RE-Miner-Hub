import logging
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.dto.SentimentDTO import SentimentDTO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EmotionService():
    def __init__(self):
        self.gpt_model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8gzGA5Sq"
        self.bert_beto_headers = {'Content-Type': 'application/json'}
        self.bert_beto_endpoint = os.environ.get('SENTIMENT_ANALYSIS_API_URL', 'http://127.0.0.1:3005') + '/api/emotion'

    def map_emotion(emotion):
        mapped_emotion = ''
        if emotion == 'angry':
            mapped_emotion = 'anger'
        elif emotion == 'happy':
            mapped_emotion = 'happiness'
        elif emotion == 'sad':
            mapped_emotion = 'sadness'
        elif emotion == 'surprise':
            mapped_emotion = 'surprise'
        elif emotion == 'disgust':
            mapped_emotion = 'disgust'
        elif emotion == 'not-relevant':
            mapped_emotion = 'Not relevant'
        else:
            mapped_emotion = emotion
        return mapped_emotion

    def analyze_sentence_with_gpt(self, sentence):
        result = {}
        completion = client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": "Can you tell me what emotion is expressing the review above? It can be one of the following: happiness, sadness, anger, fear, surprise or disgust."},
                {"role": "user", "content": sentence}
            ]
        )
        if completion is None:
            return "An error occurred"
        result = {'emotion': completion.choices[0].message.content}
        return result

    def analyze_sentence_with_BERT_BETO(self, model, sentence):
        response = requests.post(self.endpoint, params={'tool': model}, headers=self.headers, json={'text': sentence})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise Exception("Error in sentiment analysis request")
        else:
            raise Exception("Error in sentiment analysis request")

    def extract_emotion_form_sentence(self, sentiment_model, sentence):
        logging.info(f"Extracting emotions with sentiment model: {sentiment_model} for sentence: {sentence}")
        if sentiment_model == 'GPT-3.5':
            detected_emotion = self.analyze_sentence_with_gpt(sentence)
            sentiment_dto = SentimentDTO(detected_emotion.get('emotion'))
        else: 
            analyzed_bert_beto_sentence = self.analyze_sentence_with_BERT_BETO(sentiment_model, sentence)
            if analyzed_bert_beto_sentence is None:
                return "Error in sentiment analysis request", 500
            elif 'emotions' in analyzed_bert_beto_sentence:
                max_emotion = max(analyzed_bert_beto_sentence['emotions'], key=analyzed_bert_beto_sentence['emotions'].get)
                mapped_emotion = self.map_emotion(max_emotion)
                if mapped_emotion == 'Not relevant':
                    max_value = 0
                    for emotion, value in analyzed_bert_beto_sentence['emotions'].items():
                        if emotion != 'not-relevant' and value > max_value:
                            max_value = value
                            mapped_emotion = self.map_emotion(emotion)
                sentiment_dto = SentimentDTO(sentiment=mapped_emotion)
        return sentiment_dto
