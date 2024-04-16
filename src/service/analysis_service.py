import logging
from src.service.emotion_service import EmotionService
from src.service.feature_service import FeatureService
from src.dto import SentenceDTO
class AnalysisService():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    def analyze_sentence_sentiments(self, sentiment_model, sentence: SentenceDTO):
        emotion_service = EmotionService()
        sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
        sentence.sentimentData = sentiment

    def analyze_sentence_features(self, feature_model, sentence):
        feature_service = FeatureService()
        feature = feature_service.extract_feature_from_sentence(feature_model, sentence.text)
        sentence.featureData = feature

    def analyze_review_sentences(self, sentiment_model, feature_model, review):
        for index, sentence in enumerate(review.sentences):
            if sentence.text is not None:
                if sentiment_model is not None:
                    self.analyze_sentence_sentiments(sentiment_model, sentence)
                if feature_model is not None:
                    self.analyze_sentence_features(feature_model, sentence)
                
    def analyze_reviews(self, sentiment_model, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            self.analyze_review_sentences(sentiment_model, feature_model, review_dto)
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews