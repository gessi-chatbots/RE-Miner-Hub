import json
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from transformers import pipeline
from src.emotion_extraction_service import EmotionExtractionService
from src.feature_extraction_service import FeatureExtractionService
from src.sentiment_analysis_service import SentimentAnalysisService
from dto import FeatureDTO, SentimentDTO, SentenceDTO, ReviewResponseDTO

import logging




    
logging.basicConfig(level=logging.DEBUG)

def format_features(text, ner_results):
    features = []
    current_feature = ""

    for feature in ner_results:
        start = feature['start']
        end = feature['end']

        # Hot fix to get the whole word
        blank_space = False
        while start > 0 and not blank_space and not text[start] == ' ':
            if text[start - 1] != ' ':
                start -= 1
            else:
                blank_space = True

        blank_space = False
        while end < len(text) - 1 and not blank_space and not text[end] == ' ':
            if text[end + 1] != ' ':
                end += 1
            else:
                blank_space = True

        f = text[start:end + 1]

        if feature['entity'] == 'B-feature':
            # If we were processing a feature, it is saved
            if len(current_feature) > 0:
                features.append(current_feature.strip().lower())
                current_feature = ""
            # current_feature += f + " "
            current_feature += f

        elif feature['entity'] == 'I-feature':
            # hot fix to make sure a feature does not have the same word twice
            if f not in current_feature:
                current_feature += f + " "

        elif feature['entity'] == 'O':
            # If we were processing a feature, it is saved
            if len(current_feature) > 0:
                features.append(current_feature.strip().lower())
                current_feature = ""

    if len(current_feature) > 0:
        features.append(current_feature.strip().lower())
    return features


app = Flask(__name__)
CORS(app)


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
        'app_name': "API emotion extraction"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route('/extract-emotion', methods=['POST'])
def extract_emotion():
    try:
        if not request.args or 'model_emotion' not in request.args.keys() and 'text' not in request.json.keys():
            return "Lacking model and textual data in proper tag.", 400
        if 'model_emotion' not in request.args.keys():
            return "Lacking model in proper tag.", 400
        if 'text' not in request.json.keys():
            return "Lacking textual data in proper tag.", 400

        model = request.args.get("model_emotion")
        data = request.get_json()
        text = data.get("text")

        other_models = ["BERT", "BETO"]

        results = {}

        if model == "GPT-3.5":
            emotion_extraction_handler = EmotionExtractionService()
            reviews_with_emotion = emotion_extraction_handler.emotion_extraction(text)
            for review in reviews_with_emotion:
                id_text = review['text']['id']
                results[id_text] = {
                    "text": review['text']
                }
                results[id_text]['text']['emotion'] = review['emotion']
        elif model in other_models:
            api_sentiment_analysis = SentimentAnalysisService()
            for message in text:
                emotions = api_sentiment_analysis.get_emotions(model, message['text'])
                if emotions is None:
                    return "Error in sentiment analysis request", 500
                else:
                    results[message['id']] = {
                        "text": message
                    }
                max_emotion = max(emotions['emotions'], key=emotions['emotions'].get)
                results[message['id']]['text']['emotion'] = max_emotion
                results[message['id']]['text']['emotions'] = emotions['emotions']
        else:
            return "Model not found", 404

        results = list(results.values())

        return jsonify(results)

    except Exception as e:
        return f"An error occurred: {e}", 400


@app.route('/extract-features', methods=['POST'])
def extract_features():
    try:
        if not request.args or 'model_features' not in request.args.keys() and 'text' not in request.json.keys():
            return "Lacking model and textual data in proper tag.", 400
        if 'model_features' not in request.args.keys():
            return "Lacking model in proper tag.", 400
        if 'text' not in request.json.keys():
            return "Lacking textual data in proper tag.", 400

        model = request.args.get("model_features")
        data = request.get_json()
        text = data.get("text")

        other_models = ["t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base",
                        "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]

        features_with_id = []
        results = {}

        for message in text:
            results[message['id']] = {
                "text": message
            }

        if model == "transfeatex":
            api_feature_extraction = FeatureExtractionService()
            features_with_id = api_feature_extraction.extract_features(text)
        elif model in other_models:
            for message in text:
                classifier = pipeline("ner", model="quim-motger/" + model)
                ner_results = classifier(message['text'])
                features = format_features(message['text'], ner_results)
                features_with_id.append({'id': message['id'], 'features': features})
        else:
            return "Model not found", 404

        for review in features_with_id:
            id_text = review['id']
            if id_text in results:
                results[id_text]['text']['features'] = review['features']

        results = list(results.values())

        return jsonify(results)

    except Exception as e:
        return f"An error occurred: {e}", 400


def map_emotion(emotion):
    mapped_emotion = ''
    if emotion == 'angry':
        mapped_emotion = 'anger'
    elif emotion == 'happy':
        mapped_emotion = 'happiness'
    elif emotion == 'sad':
        mapped_emotion = 'sadness'
    elif emotion == 'surprise':
        mapped_emotion = 'surprise'
    elif emotion == 'disgust':
        mapped_emotion = 'disgust'
    elif emotion == 'not-relevant':
        mapped_emotion = 'Not relevant'
    else:
        mapped_emotion = emotion
    return mapped_emotion

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
                reviews_dict = {}
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
                    features = format_features(sentence.text, ner_results)
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
    
@app.route('/analyze-reviews', methods=['POST'])
@DeprecationWarning
def analyze():
    try:
        if not request.args \
                or ('model_emotion' not in request.args.keys() and 'model_features' not in request.args.keys()) \
                and 'text' not in request.json.keys():
            return "Lacking model and textual data in proper tag.", 400
        if 'model_emotion' not in request.args.keys() and 'model_features' not in request.args.keys():
            return "Lacking model in proper tag.", 400
        if 'text' not in request.json.keys():
            return "Lacking textual data in proper tag.", 400
        print("Request received")
        model_emotion = request.args.get("model_emotion", None)
        model_features = request.args.get("model_features", None)
        data = request.get_json()
        texts = data.get("text")
        other_models_emotion = ["BERT", "BETO"]
        other_models_features = ["t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base",
                                 "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]
        results = {}
        for text in texts:
            id_text = text['id']
            results[id_text] = {
                "text": {
                    'text': text['text'],
                    "emotions": [],
                    "features": []
                }
            }
        features_with_id = []


        if model_emotion != '' and model_emotion == "GPT-3.5":
            emotion_extraction_handler = EmotionExtractionService()
            reviews_with_emotion = emotion_extraction_handler.emotion_extraction(texts)
            for review in reviews_with_emotion:
                id_text = review['text']['id']
                results[id_text]['text']['text'] = review['text']['text']
                results[id_text]['text']['emotions'].append(review['emotion'])
        elif model_emotion != '' and model_emotion in other_models_emotion:
            api_sentiment_analysis = SentimentAnalysisService()
            for message in texts:
                emotions = api_sentiment_analysis.get_emotions(model_emotion, message['text'])
                if emotions is None:
                    return "Error in sentiment analysis request", 500
                else:
                    max_emotion = max(emotions['emotions'], key=emotions['emotions'].get)
                    results[id_text]['text']['text'] = message
                    mapped_emotion = map_emotion(max_emotion)
                    if mapped_emotion == 'Not relevant':
                        max_value = 0
                        for emotion, value in emotions['emotions'].items():
                            if emotion != 'not-relevant' and value > max_value:
                                max_value = value
                                mapped_emotion = map_emotion(emotion)
                    results[id_text]['text']['emotions'].append(mapped_emotion)
        if model_features != '' and model_features == "transfeatex":
            api_feature_extraction = FeatureExtractionService()
            features_with_id = api_feature_extraction.extract_features(texts)
        elif model_features != '' and model_features in other_models_features:
            for message in texts:
                classifier = pipeline("ner", model="quim-motger/" + model_features)
                ner_results = classifier(message['text'])
                features = format_features(message['text'], ner_results)
                features_with_id.append({'id': message['id'], 'features': features})


        for review in features_with_id:
            id_text = review['id']
            if id_text in results:
                features_to_append = review.get('features', [])
                if isinstance(features_to_append, list):
                    if 'text' in results[id_text]:
                        for feature_to_append in features_to_append:
                            results[id_text]['text']['features'].append(feature_to_append)
                    else:
                        print(f"Invalid structure for id_text {id_text}. 'text' or 'features' key missing.")
                else:
                    print(
                        f"Invalid 'features' type for id_text {id_text}. Expected list, got {type(features_to_append)}.")
            else:
                print(f"Id_text {id_text} not found in results.")

        results = list(results.values())
        print(f"Feature Model: {model_features}, Sentiment Model: {model_emotion}Result: {results}")
        return jsonify(results)

    except Exception as e:
        return f"An error occurred: {e}", 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
