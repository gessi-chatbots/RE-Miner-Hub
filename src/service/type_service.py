import logging
import requests
import os
from dotenv import load_dotenv
from src.dto.TypeDTO import TypeDTO
from src.dto.LanguageModelDTO import LanguageModelDTO

load_dotenv()

class TypeService():
    def __init__(self):
        self.bert_roberta_distilbert_endpoint = os.environ.get('TYPE_ANALYSIS_API_URL', 'http://127.0.0.1:3011') + '/analyze-type'
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_sentence_with_BERT_ROBERTA_DISTILBERT(self, model, sentence):
        headers = {'Authorization': os.getenv("AUTHORIZATION_KEY"), 'Content-Type': 'application/json'}
        response = requests.post(self.bert_roberta_distilbert_endpoint, params={'type-service': model}, headers=headers, json={'text': sentence})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise Exception("Error in sentiment analysis request")
        else:
            raise Exception("Error in sentiment analysis request")

    def extract_type_form_sentence(self, type_model, sentence):
        logging.info(f'Extracting type with model: {type_model} for sentence: "{sentence}"')
        if type_model == 'BERT' or type_model == 'ROBERTA' or type_model == 'DISTILBERT':
            review = self.analyze_sentence_with_BERT_ROBERTA_DISTILBERT(sentence)
            type_dto = TypeDTO(review.get('type'), languageModel=LanguageModelDTO(modelName=type_model))
            return sentiment_dto
        else:
            logger.info(f'Type model {type_model} not supported')
            return None
