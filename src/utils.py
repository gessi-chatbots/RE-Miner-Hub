from src.dto.SentenceDTO import SentenceDTO
from src.dto.SentimentDTO import SentimentDTO
from src.dto.FeatureDTO import FeatureDTO
from src.dto.PolarityDTO import PolarityDTO
from src.dto.TypeDTO import TypeDTO
from src.dto.TopicDTO import TopicDTO
from src.dto.ReviewResponseDTO import ReviewResponseDTO
import logging

logger = logging.getLogger(__name__)

def extractReviewDTOsFromJson(reviews_dict):
    review_dto_list = []
    logger.info(reviews_dict)
    for review in reviews_dict:
        id = review.get('reviewId')
        body = review.get('review')
        sentences_json = review.get('sentences')
        sentences = []
        if sentences_json is not None:
            for sentence_json in sentences_json:
                sentence = SentenceDTO(id=sentence_json.get('id'), sentimentData=None, featureData=None, polarityData=None, typeData=None, topicData=None, text=sentence_json.get('text'))
                if 'sentimentData' in sentence_json:
                    sentimentData = sentence_json.get('sentimentData', None)
                    if sentimentData is not None:
                        sentimentDTO = SentimentDTO(sentiment=sentimentData.get('sentiment'))
                        sentence.sentimentData = sentimentDTO
                if 'featureData' in sentence_json: 
                    featureData = sentence_json.get('featureData', None)
                    if featureData is not None:
                        featureDTO = FeatureDTO(feature=featureData.get('feature'))
                        sentence.featureData = featureDTO
                if 'polarityData' in sentence_json:
                    polarityData = sentence_json.get('polarityData', None)
                    if polarityData is not None:
                        polarityDTO = PolarityDTO(polarity=polarityData.get('polarity'))
                        sentence.polarityData = polarityDTO
                if 'typeData' in sentence_json:
                    typeData = sentence_json.get('typeData', None)
                    if typeData is not None:
                        typeDTO = TypeDTO(type=typeData.get('type'))
                        sentence.typeData = typeDTO
                if 'topicData' in sentence_json:
                    topicData = sentence_json.get('topicData', None)
                    if topicData is not None:
                        topicDTO = TopicDTO(topic=topicData.get('topic'))
                        sentence.topicData = topicDTO
                sentences.append(sentence)
        review_dto = ReviewResponseDTO(id=id, review=body, sentences=sentences)
        review_dto_list.append(review_dto)
    return review_dto_list

def extract_reviews_from_json_new_version(sentences_dict):
    sentences_list = []
    for sentence in sentences_dict:
        id = sentence.get('id')
        sentence_text = sentence.get('sentence')
        sentence = SentenceDTO(id=id, sentimentData=None, featureData=None, text=sentence_text)
        sentences_list.append(sentence)
    return sentences_list