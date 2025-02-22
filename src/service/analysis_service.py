import logging
import src.service.review_service as revSv
from src.service.emotion_service import EmotionService
from src.service.feature_service import FeatureService
from src.service.polarity_service import PolarityService
from src.service.type_service import TypeService
from src.service.topic_service import TopicService
from src.dto import SentenceDTO
from multiprocessing import Pool
import time

def analyze_sentiment(sentiment_model, sentence):
    if sentiment_model is not None:
        return analyze_sentence_sentiments(sentiment_model, sentence)

def analyze_feature(feature_model, sentence):
    if feature_model is not None:
        return analyze_sentence_features(feature_model, sentence)


def analyze_sentence_sentiments(sentiment_model, sentence: SentenceDTO):
    emotion_service = EmotionService()
    start_time = time.time()
    sentiment = emotion_service.extract_emotion_form_sentence(sentiment_model, sentence.text)
    end_time = time.time()
    sentiment.extraction_time = end_time - start_time
    sentence.sentimentData = sentiment
    return sentence

def analyze_sentence_features(feature_model, sentence):
    feature_service = FeatureService()
    start_time = time.time()
    feature = feature_service.extract_feature_from_sentence(feature_model, sentence.text)
    end_time = time.time()
    feature.extraction_time = end_time - start_time
    feature.feature = to_camel_case(feature.feature)
    sentence.featureData = feature
    return sentence

def analyze_sentence_polarity(polarity_model, sentence):
    polarity_service = PolarityService()
    start_time = time.time()
    polarity = polarity_service.extract_polarity_form_sentence(polarity_model, sentence.text)
    end_time = time.time()
    polarity.extraction_time = end_time - start_time
    sentence.polarityData = polarity
    return sentence

def analyze_sentence_type(type_model, sentence):
    type_service = TypeService()
    start_time = time.time()
    type = type_service.extract_type_form_sentence(type_model, sentence.text)
    end_time = time.time()
    type.extraction_time = end_time - start_time
    sentence.typeData = type
    return sentence

def analyze_sentence_topic(topic_model, sentence):
    topic_service = TopicService()
    start_time = time.time()
    topic = topic_service.extract_topic_form_sentence(topic_model, sentence.text)
    end_time = time.time()
    topic.extraction_time = end_time - start_time
    sentence.topicData = topic
    return sentence  

def to_camel_case(sentence):
    words = sentence.split()
    camel_case_sentence = ''.join(word.capitalize() for word in words)
    return camel_case_sentence
    
class AnalysisService():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def analyze_review_sentences(self, sentiment_model, feature_model, polarity_model, type_model, topic_model, sentences):
        for sentence in sentences:
            start = time.time()
            if sentence.text is not None:
                if sentiment_model is not None:
                    analyze_sentence_sentiments(sentiment_model, sentence)
                if feature_model is not None:
                    analyze_sentence_features(feature_model, sentence)
                if polarity_model is not None:
                    analyze_sentence_polarity(polarity_model, sentence)
                if type_model is not None:
                    analyze_sentence_type(type_model, sentence)
                if topic_model is not None:
                    analyze_sentence_topic(topic_model, sentence)
            sentence.extraction_time = time.time() - start
            print(sentence)
        return sentences
    
    def analyze_review_sentences_multiprocess(self, sentiment_model, feature_model, polarity_model, type_model, topic_model, sentences):
        num_processes = 2
        with Pool(processes=num_processes) as pool:
            results = []
            for sentence in sentences:
                start = time.time()
                if sentiment_model is not None:
                    sentiment_result = pool.apply_async(analyze_sentiment, args=(sentiment_model, sentence))
                    results.append(sentiment_result)
                if feature_model is not None:
                    feature_result = pool.apply_async(analyze_feature, args=(feature_model, sentence))
                    results.append(feature_result)
                if polarity_model is not None:
                    polarity_result = pool.apply_async(analyze_polarity, args=(polarity_model, sentence))
                    results.append(polarity_result)
                if type_model is not None:
                    type_result = pool.apply_async(analyze_type, args=(type_model, sentence))
                    results.append(type_result)
                if topic_model is not None:
                    topic_result = pool.apply_async(analyze_topic, args=(topic_model, sentence))
                    results.append(topic_result)
            combined_results = [result.get() for result in results]
            sentence.extraction_time = time.time() - start

        return [sentence.to_dict() for sentence in combined_results]
    
    def analyze_reviews_kg(self, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            revSv.add_sentences_to_review(review_dto)
            analyzed_sentences = self.analyze_review_sentences(None,
                                                               feature_model,
                                                               review_dto.sentences)
            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews

    def analyze_reviews(self, sentiment_model, feature_model, polarity_model, type_model, topic_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            revSv.check_review_splitting(review_dto)

            analyzed_sentences = self.analyze_review_sentences(
                sentiment_model,
                feature_model,
                polarity_model,
                type_model,
                topic_model,
                review_dto.sentences
            )

            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())

        return analyzed_reviews

    def test_performance_analyze_reviews(self, sentiment_model, feature_model, polarity_model, type_model, topic_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            analyzed_sentences = self.analyze_review_sentences_v1(sentiment_model, feature_model, polarity_model, type_model, topic_model, review_dto.sentences)
            review_dto.sentences = analyzed_sentences
            analyzed_reviews.append(review_dto.to_dict())
        return analyzed_reviews
