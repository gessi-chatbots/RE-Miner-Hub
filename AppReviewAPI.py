import flask
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from transformers import pipeline

from src.emotion_extraction_handler import EmotionExtractionHandler
from src.API_feature_extraction import APIFeatureExtraction
from src.API_sentiment_analysis import APISentimentAnalysis

def format_features(text, ner_results):	
	features = []
	current_feature = ""

	for feature in ner_results:
		start = feature['start']
		end = feature['end']

		# Hot fix to get the whole word
		blank_space = False
		while start > 0 and not blank_space and not text[start] == ' ':
			if text[start-1] != ' ':
				start -= 1
			else:
				blank_space = True

		blank_space = False
		while end < len(text)-1 and not blank_space and not text[end] == ' ':
			if text[end+1] != ' ':
				end += 1
			else:
				blank_space = True

		f = text[start:end+1]

		if feature['entity'] == 'B-feature':
			#If we were processing a feature, it is saved
			if len(current_feature) > 0:
				features.append(current_feature.strip().lower())
				current_feature = ""
			current_feature += f + " "

		elif feature['entity'] == 'I-feature':
			# hot fix to make sure a feature does not have the same word twice
			if f not in current_feature:
				current_feature += f + " "

		elif feature['entity'] == 'O':
			#If we were processing a feature, it is saved
			if len(current_feature) > 0:
				features.append(current_feature.strip().lower())
				current_feature = ""

	if len(current_feature) > 0:
		features.append(current_feature.strip().lower())

	return features

def create_app():
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

            other_models = ["ParallelDots", "BERT", "BETO", "SVC"]

            results = {}

            if model == "GPT-3.5":
                emotion_extraction_handler = EmotionExtractionHandler()
                reviews_with_emotion = emotion_extraction_handler.emotion_extraction(text)
                for review in reviews_with_emotion:
                    id_text = review['text']['id']
                    results[id_text] = {
                        "emotion": review['emotion'],
                        "text": review['text']
                    }
            elif model in other_models:
                api_sentiment_analysis = APISentimentAnalysis()
                for message in text:
                    emotions = api_sentiment_analysis.get_emotions(model, message['text'])
                    if emotions is None:
                        return "Error in sentiment analysis request", 500
                    else:
                        results[message['id']] = {
                            "emotions": emotions['emotions'],
                            "text": message
                        }
                    max_emotion = max(emotions['emotions'], key=emotions['emotions'].get)
                    results[message['id']]['emotion'] = max_emotion
            else:
                return "Model not found", 404

            results = list(results.values())

            return jsonify(results)

        except Exception as e:
            return f"An error occurred: {e}"

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

            other_models = ["t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base", "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]

            features_with_id = []
            results = {}

            for message in text:
                results[message['id']] = {
                    "text": message
                }

            if model == "transfeatex":
                api_feature_extraction = APIFeatureExtraction()
                features_with_id = api_feature_extraction.extract_features(text)
            elif model in other_models:
                for message in text:
                    classifier = pipeline("ner", model="quim-motger/"+model)
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

    @app.route('/analyze-reviews', methods=['POST'])
    def analyze_reviews():
        try:
            if not request.args or ('model_emotion' or 'model_features' not in request.args.keys()) and 'text' not in request.json.keys():
                return "Lacking model and textual data in proper tag.", 400
            if ('model_emotion' or 'model_features') not in request.args.keys():
                return "Lacking model in proper tag.", 400
            if 'text' not in request.json.keys():
                return "Lacking textual data in proper tag.", 400
            
            model_emotion = request.args.get("model_emotion")
            model_features = request.args.get("model_features")
            data = request.get_json()
            text = data.get("text")

            other_models_emotion = ["ParallelDots", "BERT", "BETO", "SVC"]
            other_models_features = ["t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base", "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]

            features_with_id = []
            results = {}

            if model_emotion == "GPT-3.5":
                emotion_extraction_handler = EmotionExtractionHandler()
                reviews_with_emotion = emotion_extraction_handler.emotion_extraction(text)
                for review in reviews_with_emotion:
                    id_text = review['text']['id']
                    results[id_text] = {
                        "emotion": review['emotion'],
                        "text": review['text']
                    }
            elif model_emotion in other_models_emotion:
                api_sentiment_analysis = APISentimentAnalysis()
                for message in text:
                    emotions = api_sentiment_analysis.get_emotions(model_emotion, message['text'])
                    if emotions is None:
                        return "Error in sentiment analysis request", 500
                    else:
                        results[message['id']] = {
                            "emotions": emotions['emotions'],
                            "text": message
                        }
                    max_emotion = max(emotions['emotions'], key=emotions['emotions'].get)
                    results[message['id']]['emotion'] = max_emotion
            else:
                return "Model not found", 404

            if model_features == "transfeatex":
                api_feature_extraction = APIFeatureExtraction()
                features_with_id = api_feature_extraction.extract_features(text)
            elif model_features in other_models_features:
                for message in text:
                    classifier = pipeline("ner", model="quim-motger/"+model_features)
                    ner_results = classifier(message['text'])
                    features = format_features(message['text'], ner_results)
                    features_with_id.append({'id': message['id'], 'features': features})
            else:
                return "Model not found", 404

            for review in features_with_id:
                id_text = review['id']
                if id_text in results:
                    results[id_text]['features'] = review['features']

            results = list(results.values())

            return jsonify(results)

        except Exception as e:
            return f"An error occurred: {e}", 500

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host='0.0.0.0', port=3000)