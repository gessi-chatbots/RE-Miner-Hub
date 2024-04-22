import logging
import time
from src.service.emotion_service import EmotionService
from src.service.feature_service import FeatureService
from src.dto import SentenceDTO
class PerformanceService():

    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_sentence_sentiments(self, sentiment_model, sentence: SentenceDTO):
        emotion_service = EmotionService()
        sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
        sentence.sentimentData = sentiment

    def analyze_sentence_features(self, feature_model, sentence):
        feature_service = FeatureService()
        feature = feature_service.extract_feature_from_sentence(feature_model, sentence.text)
        sentence.featureData = feature

    def test_performance_analysis_review_sentences(self, sentiment_model, feature_model, review):
        review_performance_data = []
        for index, sentence in enumerate(review.sentences):
            if sentence.text is not None:
                sentence_performance_data = {'sentence_id': sentence.id}
                start_sentence_time = time.time()
                if sentiment_model is not None:
                    start_sentiment_time = time.time()
                    self.analyze_sentence_sentiments(sentiment_model, sentence)
                    end_sentiment_time = time.time()
                    sentence_performance_data['sentence_sentiment_analysis_time'] = end_sentiment_time - start_sentiment_time
                if feature_model is not None:
                    start_feature_time = time.time()
                    self.analyze_sentence_features(feature_model, sentence)
                    end_feature_time = time.time()
                    sentence_performance_data['sentence_feature_analysis_time'] = end_feature_time - start_feature_time
                end_sentence_time = time.time()
                sentence_performance_data['sentence_total_analysis_time'] = end_sentence_time - start_sentence_time
                review_performance_data.append(sentence_performance_data)
        return review_performance_data

                
                
    def test_performance_analysis_reviews(self, sentiment_model, feature_model, review_dto_list):
        performance_data = {'reviews':[]}
        total_start_time = time.time()
        for review_dto in review_dto_list:
            review_performance_result = {'review_id': review_dto.reviewId}
            start_review_time = time.time()
            review_performance_result['sentences'] = self.test_performance_analysis_review_sentences(sentiment_model, feature_model, review_dto)
            end_review_time = time.time()
            review_performance_result['review_total_analysis_time'] = end_review_time - start_review_time 
            performance_data['reviews'].append(review_performance_result)
        total_end_time = time.time()
        performance_data["total_analysis_time"] = total_end_time-total_start_time
        return performance_data