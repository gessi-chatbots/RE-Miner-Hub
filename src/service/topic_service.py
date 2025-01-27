import logging
import requests
import os
from dotenv import load_dotenv
from src.dto.TopicDTO import TopicDTO
from src.dto.LanguageModelDTO import LanguageModelDTO

load_dotenv()

class TopicService():
    def __init__(self):
        self.svm_mlp_endpoint = os.environ.get('TOPIC_ANALYSIS_API_URL', 'http://127.0.0.1:3012') + '/analyze-topic'
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_sentence_with_SVM_MLP(self, model, sentence):
        headers = {'Authorization': os.getenv("AUTHORIZATION_KEY"), 'Content-Type': 'application/json'}
        response = requests.post(self.svm_mlp_endpoint, params={'topic-service': model}, headers=headers, json={'text': sentence})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise Exception("Error in topic analysis request")
        else:
            raise Exception("Error in topic analysis request")

    def extract_topic_form_sentence(self, topic_model, sentence):
        logging.info(f'Extracting topic with model: {topic_model} for sentence: "{sentence}"')
        if topic_model == 'SVM' or topic_model == 'MLP':
            review = self.analyze_sentence_with_SVM_MLP(topic_model, sentence)
            topic_dto = TopicDTO(review.get('topic'), languageModel=LanguageModelDTO(modelName=topic_model))
            return topic_dto
        else:
            logger.info(f'Topic model {topic_model} not supported')
            return None
