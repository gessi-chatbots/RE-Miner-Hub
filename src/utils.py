from src.dto.SentenceDTO import SentenceDTO
from src.dto.SentimentDTO import SentimentDTO
from src.dto.FeatureDTO import FeatureDTO
from src.dto.ReviewResponseDTO import ReviewResponseDTO

def extractReviewDTOsFromJson(reviews_dict):
    review_dto_list = []
    for review in reviews_dict:
        id = review.get('reviewId')
        body = review.get('review')
        sentences_json = review.get('sentences')
        sentences = []
        if sentences_json is not None:
            for sentence_json in sentences_json:
                sentence = SentenceDTO(id=sentence_json.get('id'), sentimentData=None, featureData=None, text=sentence_json.get('text'))
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
                sentences.append(sentence)
        review_dto = ReviewResponseDTO(id=id, review=body, sentences=sentences)
        review_dto_list.append(review_dto)
    return review_dto_list

def extract_reviews_from_json_new_version(sentences_dict):
    review_dto_list = []
    for sentence in sentences_dict:
        id = review.get('reviewId')
        body = review.get('review')
        sentences_json = review.get('sentences')
        sentences = []
        if sentences_json is not None:
            for sentence_json in sentences_json:
                sentence = SentenceDTO(id=sentence_json.get('id'), sentimentData=None, featureData=None, text=sentence_json.get('text'))
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
                sentences.append(sentence)
        review_dto = ReviewResponseDTO(id=id, review=body, sentences=sentences)
        review_dto_list.append(review_dto)
    return review_dto_list