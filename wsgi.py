import json
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from transformers import pipeline
from src.emotion_extraction_service import EmotionExtractionService
from src.feature_extraction_service import FeatureExtractionService
from src.sentiment_analysis_service import SentimentAnalysisService
from dto import FeatureDTO, SentimentDTO, SentenceDTO, ReviewResponseDTO
from service.feature_service import FeatureService
from exceptions import api_exceptions
from service.emotion_service import map_emotion
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

@app.route('/swagger.yaml')
def swagger_yaml():
    return send_file('swagger.yaml')

# Flask Swagger configs
SWAGGER_URL = '/swagger'
API_URL = '/swagger.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "RE-Miner HUB"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.handle_exception(api_exceptions.TransfeatExException)
def handle_transfeatex_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

@app.handle_exception(api_exceptions.RequestException)
def handle_request_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)


@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    try:
        if not request.args \
                or ('sentiment_model' not in request.args.keys() and 'feature_model' not in request.args.keys()) \
                and 'text' not in request.json.keys():
            return "Lacking model and textual data in proper tag.", 400
        if 'sentiment_model' not in request.args.keys() and 'feature_model' not in request.args.keys():
            return "Lacking model in proper tag.", 400

        sentiment_model = request.args.get("sentiment_model", None)
        feature_model = request.args.get("feature_model", None)
        expected_sentiment_models = ["BERT", "BETO", "GPT-3.5"]
        expected_feature_models = ["transfeatex", "t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base",
                                 "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]
        if sentiment_model is not None and sentiment_model not in expected_sentiment_models:
            return make_response(jsonify({'message': 'Unknown sentiment model'}), 400)       
        if feature_model is not None and feature_model not in expected_feature_models:
            return make_response(jsonify({'message': 'Unknown sentiment model'}), 400)
        
        reviews = request.get_json()
        
        if reviews is None:
            return make_response(jsonify({'message': 'no reviews submitted for analysis'}), 400)
        if isinstance(reviews, str):
            try:
                reviews_dict = json.loads(reviews)
            except json.decoder.JSONDecodeError:
                raise Exception("Error in decoding request")
        else:
            reviews_dict = reviews


        analyzed_reviews = []
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

            for index, sentence in enumerate(review_dto.sentences):
                if sentence.text is not None and sentiment_model != '' and sentiment_model == "GPT-3.5":
                    emotion_extraction_handler = EmotionExtractionService()
                    sentence_sentiment = emotion_extraction_handler.emotion_extraction_aux(sentence.text)
                    if sentence_sentiment is not None:
                        sentiment =  sentence_sentiment["emotion"]
                        sentiment_dto = SentimentDTO(sentiment=sentiment)
                        sentence.sentimentData = sentiment_dto
                elif sentence.text is not None and sentiment_model != '' and sentiment_model in expected_sentiment_models:
                    api_sentiment_analysis = SentimentAnalysisService()
                    emotions = api_sentiment_analysis.get_emotions(sentiment_model, sentence.text)
                    if emotions is None:
                        return "Error in sentiment analysis request", 500
                    elif 'emotions' in emotions:
                        max_emotion = max(emotions['emotions'], key=emotions['emotions'].get)
                        mapped_emotion = map_emotion(max_emotion)
                        if mapped_emotion == 'Not relevant':
                            max_value = 0
                            for emotion, value in emotions['emotions'].items():
                                if emotion != 'not-relevant' and value > max_value:
                                    max_value = value
                                    mapped_emotion = map_emotion(emotion)
                        sentiment_dto = SentimentDTO(sentiment=mapped_emotion)
                        sentence.sentimentData = sentiment_dto
                features = []
                if sentence.text is not None and feature_model != '' and feature_model == "transfeatex":
                    logging.debug("Using transfeatex for feature extraction")
                    api_feature_extraction = FeatureExtractionService()
                    features = api_feature_extraction.extract_features(sentence.text)
                elif sentence.text is not None and feature_model != '' and feature_model in expected_feature_models:
                    logging.debug(f"Using model {feature_model} for NER")
                    classifier = pipeline("ner", model="quim-motger/" + feature_model)
                    ner_results = classifier(sentence.text)
                    feature_service = FeatureService()
                    features = feature_service.format_features(sentence.text, ner_results)
                if features is not None and len(features) > 0:
                    feature = features[0] # TODO discuss if multiple features
                    feature_dto = FeatureDTO(feature=feature)
                    sentence.featureData = feature_dto
                    # features_with_id.append({'id': sentence['id'], 'features': features})
            analyzed_reviews.append(review_dto.to_dict())
        return make_response(analyzed_reviews, 200)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
