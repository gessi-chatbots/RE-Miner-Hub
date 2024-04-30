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
        result = end_sentiment_time - start_sentiment_time 
        return result, "sentiment"

def analyze_feature(feature_model, sentence):
    if feature_model is not None:
        start_feature_time = time.time()
        analyze_sentence_features(feature_model, sentence)
        end_feature_time = time.time()
        result = end_feature_time - start_feature_time 
        return result, "feature"
    
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
        for sentence in sentences:
            if sentence.text is not None:
                sentence_performance_data = {'sentence_id': sentence.id}
                start_sentence_time = time.time()
                if sentiment_model is not None:
                    sentiment_start_time = time.time()
                    analyze_sentence_sentiments(sentiment_model, sentence)
                    sentiment_end_time = time.time()
                    sentence_performance_data['sentence_sentiment_analysis_time'] = sentiment_end_time - sentiment_start_time
                if feature_model is not None:
                    feature_start_time = time.time()
                    analyze_sentence_features(feature_model, sentence)
                    feature_end_time = time.time()
                    sentence_performance_data['sentence_feature_analysis_time'] = feature_end_time - feature_start_time
                end_sentence_time = time.time()
                sentence_performance_data['sentence_total_analysis_time'] = end_sentence_time - start_sentence_time
                review_performance_data.append(sentence_performance_data)  
        return review_performance_data
    


    def performance_v1(self, sentiment_model, feature_model, sentences):
        review_performance_data = []
        num_processes = 2
        with Pool(processes=num_processes) as pool:
            async_results = []
            for sentence in sentences:
                sentence_start_time = time.time()
                if sentence.text is not None:
                    sentence_performance_data = {'sentence_id': sentence.id}
                    
                    if sentiment_model is not None:
                        async_results.append(pool.apply_async(analyze_sentiment, args=(sentiment_model, sentence)))
                    if feature_model is not None:
                        async_results.append(pool.apply_async(analyze_feature, args=(feature_model, sentence)))
                    
            for async_result in async_results:
                result = async_result.get()
                time_taken, result_data = result
                if "sentiment" in result_data:
                    sentence_performance_data['sentence_sentiment_analysis_time'] = time_taken
                elif "feature" in result_data:
                    sentence_performance_data['sentence_feature_analysis_time'] = time_taken

                sentence_end_time = time.time()
                final_sentence_time = sentence_end_time - sentence_start_time
                sentence_performance_data['sentence_total_analysis_time'] = final_sentence_time
                review_performance_data.append(sentence_performance_data)  
        return review_performance_data
    
    def test_performance_analysis_review_sentences(self, version, sentiment_model, feature_model, review):
        review_performance_data = []
        if version == 'v0':
            review_performance_data = self.performance_v0(sentiment_model, feature_model, review.sentences)
        elif version == 'v1':
            review_performance_data = self.performance_v1(sentiment_model, feature_model, review.sentences)
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