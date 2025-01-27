import logging
import requests
import os
from dotenv import load_dotenv
from src.dto.PolarityDTO import PolarityDTO
from src.dto.LanguageModelDTO import LanguageModelDTO

load_dotenv()

class PolarityService():
    def __init__(self):
        self.svm_mlp_endpoint = os.environ.get('POLARITY_ANALYSIS_API_URL', 'http://127.0.0.1:3010') + '/analyze-polarity'
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_sentence_with_SVM_MLP(self, model, sentence):
        headers = {'Authorization': os.getenv("AUTHORIZATION_KEY"), 'Content-Type': 'application/json'}
        response = requests.post(self.svm_mlp_endpoint, params={'polarity-service': model}, headers=headers, json={'text': sentence})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise Exception("Error in polarity analysis request")
        else:
            raise Exception("Error in polarity analysis request")

    def extract_polarity_form_sentence(self, polarity_model, sentence):
        logging.info(f'Extracting polarity with model: {polarity_model} for sentence: "{sentence}"')
        if polarity_model == 'SVM' or polarity_model == 'MLP':
            review = self.analyze_sentence_with_SVM_MLP(polarity_model, sentence)
            polarity_dto = PolarityDTO(review.get('polarity'), languageModel=LanguageModelDTO(modelName=polarity_model))
            return polarity_dto
        else:
            logger.info(f'Polarity model {polarity_model} not supported')
            return None
