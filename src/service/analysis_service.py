import logging
from service.emotion_service import EmotionService
from service.feature_service import FeatureService
from dto import SentenceDTO
class AnalysisService():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def analyze_sentence_sentiments(sentiment_model, sentence: SentenceDTO):
    emotion_service = EmotionService()
    sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
    sentence.sentimentData = sentiment

def analyze_sentence_features(feature_model, sentence):
    feature_service = FeatureService()
    feature_service.extract_emotion_form_sentence(feature_model, sentence.text)
    

def analyze_review_sentences(sentiment_model, feature_model, review):
    for index, sentence in enumerate(review.sentences):
        if sentiment_model is not None:
            analyze_sentence_sentiments(sentiment_model, sentence)
        if feature_model is not None:
            analyze_sentence_features(feature_model, sentence)
        
def analyze_reviews(sentiment_model, feature_model, review_dto_list):
    analyzed_reviews = []
    for review_dto in review_dto_list:
        analyze_review_sentences(sentiment_model, feature_model, review_dto)
        analyzed_reviews.append(review_dto.to_dict())
    return analyzed_reviews