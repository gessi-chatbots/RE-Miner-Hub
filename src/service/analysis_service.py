import logging
import src.service.review_service as revSv
from src.service.emotion_service import EmotionService
from src.service.feature_service import FeatureService
from src.dto import SentenceDTO
from multiprocessing import Pool

def analyze_sentiment(sentiment_model, sentence):
    if sentiment_model is not None:
        return analyze_sentence_sentiments(sentiment_model, sentence)

def analyze_feature(feature_model, sentence):
    if feature_model is not None:
        return analyze_sentence_features(feature_model, sentence)
    
def analyze_sentence_sentiments(sentiment_model, sentence: SentenceDTO):
    emotion_service = EmotionService()
    sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
    sentence.sentimentData = sentiment
    return sentence

def analyze_sentence_features(feature_model, sentence):
    feature_service = FeatureService()
    feature = feature_service.extract_feature_from_sentence(feature_model, sentence.text)
    if feature is not None:
        feature.feature = to_camel_case(feature.feature)
    sentence.featureData = feature
    return sentence

def to_camel_case(sentence):
    words = sentence.split()
    camel_case_sentence = ''.join(word.capitalize() for word in words)
    return camel_case_sentence
class AnalysisService():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_review_sentences(self, sentiment_model, feature_model, sentences):
        for sentence in sentences:
            if sentence.text is not None:
                if sentiment_model is not None:
                    analyze_sentence_sentiments(sentiment_model, sentence)
                if feature_model is not None:
                    analyze_sentence_features(feature_model, sentence)
        return sentences
    
    def analyze_review_sentences_multiprocess(self, sentiment_model, feature_model, sentences):
        num_processes = 2
        with Pool(processes=num_processes) as pool:
            results = []
            for sentence in sentences:
                if sentiment_model is not None:
                    sentiment_result = pool.apply_async(analyze_sentiment, args=(sentiment_model, sentence))
                    results.append(sentiment_result)
                if feature_model is not None:
                    feature_result = pool.apply_async(analyze_feature, args=(feature_model, sentence))
                    results.append(feature_result)
            combined_results = [result.get() for result in results]
        
        return [sentence.to_dict() for sentence in combined_results]
    
    def analyze_reviews_kg(self, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            revSv.add_sentences_to_review(review_dto)
            analyzed_sentences = self.analyze_review_sentences(None, feature_model, review_dto.sentences)
            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews

    def analyze_reviews(self, sentiment_model, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            analyzed_sentences = self.analyze_review_sentences(sentiment_model, feature_model, review_dto.sentences)
            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews

    def test_performance_analyze_reviews(self, sentiment_model, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            analyzed_sentences = self.analyze_review_sentences_v1(sentiment_model, feature_model, review_dto.sentences)
            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews
