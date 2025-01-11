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


def extractReviewDTOsFromJsonAux(reviews_dict):
    review_dto_list = []

    for review in reviews_dict:
        id = review.get('reviewId')
        app_id = review.get('applicationId')  # Extract applicationId
        date = review.get('date')  # Extract date
        body = review.get('review')
        sentences_json = review.get('sentences', None)  # Handle sentences if they exist
        sentences = []

        # Process sentences if provided
        if sentences_json:
            for sentence_json in sentences_json:
                sentence = SentenceDTO(
                    id=sentence_json.get('id'),
                    text=sentence_json.get('text'),
                    sentimentData=None,
                    featureData=None
                )
                # Optional: Add sentimentData if available
                sentimentData = sentence_json.get('sentimentData', None)
                if sentimentData:
                    sentence.sentimentData = SentimentDTO(sentiment=sentimentData.get('sentiment'))

                # Optional: Add featureData if available
                featureData = sentence_json.get('featureData', None)
                if featureData:
                    sentence.featureData = FeatureDTO(feature=featureData.get('feature'))

                sentences.append(sentence)
        else:
            # Add the entire review as a single sentence if sentences are missing
            sentences.append(SentenceDTO(id=f"{id}_default", text=body, sentimentData=None, featureData=None))

        # Construct the review DTO
        review_dto = ReviewResponseDTO(
            id=id,
            review=body,
            sentences=sentences,
            extraction_time=None  # Adjust as needed if extraction time is calculated
        )
        # Attach additional fields like applicationId and date if necessary
        review_dto.app_id = app_id  # Custom attribute for applicationId
        review_dto.date = date  # Custom attribute for review date

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