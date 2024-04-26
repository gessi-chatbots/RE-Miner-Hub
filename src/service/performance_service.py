import logging
import time
from multiprocessing import Pool
from src.service.emotion_service import EmotionService
from src.service.feature_service import FeatureService
from src.dto import SentenceDTO


def analyze_sentiment(sentiment_model, sentence):
    if sentiment_model is not None:
        start_sentiment_time = time.time()
        analyze_sentence_sentiments(sentiment_model, sentence)
        end_sentiment_time = time.time()
        return end_sentiment_time - start_sentiment_time

def analyze_feature(feature_model, sentence):
    if feature_model is not None:
        start_feature_time = time.time()
        analyze_sentence_features(feature_model, sentence)
        end_feature_time = time.time()
        return end_feature_time - start_feature_time
    
def analyze_sentence_sentiments(sentiment_model, sentence: SentenceDTO):
    emotion_service = EmotionService()
    sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
    sentence.sentimentData = sentiment
    return sentence

def analyze_sentence_features(feature_model, sentence):
    feature_service = FeatureService()
    feature = feature_service.extract_feature_from_sentence(feature_model, sentence.text)
    sentence.featureData = feature
    return sentence

class PerformanceService():

    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


    def performance_v0 (self, sentiment_model, feature_model, sentences):
        review_performance_data = []
        for sentence in enumerate(sentences):
            if sentence.text is not None:
                sentence_performance_data = {'sentence_id': sentence.id}
                start_sentence_time = time.time()
                if sentiment_model is not None:
                    result_sentiment_time = self.analyze_sentence_sentiments(sentiment_model, sentence)
                    sentence_performance_data['sentence_sentiment_analysis_time'] = result_sentiment_time
                if feature_model is not None:
                    result_feature_time = self.analyze_sentence_features(feature_model, sentence)
                    sentence_performance_data['sentence_feature_analysis_time'] = result_feature_time
                end_sentence_time = time.time()
                sentence_performance_data['sentence_total_analysis_time'] = end_sentence_time - start_sentence_time
                review_performance_data.append(sentence_performance_data)  
    

    def performance_v1 (self, sentiment_model, feature_model, sentences):
        review_performance_data = []
        num_processes = 2
        with Pool(processes=num_processes) as pool:
            for sentence in enumerate(sentences):
                if sentence.text is not None:
                    sentence_performance_data = {'sentence_id': sentence.id}
                    start_sentence_time = time.time()
                    if sentiment_model is not None:
                        result_sentiment_time = pool.apply_async(analyze_sentiment, args=(sentiment_model, sentence))
                        sentence_performance_data['sentence_sentiment_analysis_time'] = result_sentiment_time
                    if feature_model is not None:
                        result_feature_time = pool.apply_async(analyze_feature, args=(feature_model, sentence))
                        sentence_performance_data['sentence_feature_analysis_time'] = result_feature_time
                    end_sentence_time = time.time()
                    sentence_performance_data['sentence_total_analysis_time'] = end_sentence_time - start_sentence_time
                    review_performance_data.append(sentence_performance_data)  
        return review_performance_data
    
    def test_performance_analysis_review_sentences(self, version, sentiment_model, feature_model, review):
        review_performance_data = []
        if version == 'v0':
            review_performance_data = self.performance_v0
        elif version == 'v1':
            review_performance_data = self.performance_v1
        return review_performance_data
            
    def test_performance_analysis_reviews(self, version, sentiment_model, feature_model, review_dto_list):
        performance_data = {'reviews':[]}
        total_start_time = time.time()
        for review_dto in review_dto_list:
            review_performance_result = {'review_id': review_dto.reviewId}
            start_review_time = time.time()
            review_performance_result['sentences'] = self.test_performance_analysis_review_sentences(version, sentiment_model, feature_model, review_dto)
            end_review_time = time.time()
            review_performance_result['review_total_analysis_time'] = end_review_time - start_review_time 
            performance_data['reviews'].append(review_performance_result)
        total_end_time = time.time()
        performance_data["total_analysis_time"] = total_end_time-total_start_time
        return performance_data