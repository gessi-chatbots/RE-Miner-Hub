import flask
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from src.emotion_extraction_handler import EmotionExtractionHandler
from src.APIFeatureExtraction import APIFeatureExtraction

app = Flask(__name__)
CORS(app)

def create_app():

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

    @app.route('/analyze-reviews', methods=['POST'])
    def analyze_reviews():
        try:
            if 'model' not in request.args.keys():
                return "Lacking model in proper tag.", 400
            if 'text' not in request.json.keys():
                return "Lacking textual data in proper tag.", 400
            
            model = request.args.get("model")
            data = request.get_json()
            text = data.get("text")

            other_models = ["ParallelDots", "BERT", "BETO", "SVC"]

            if model == "GPT-3.5":
                emotion_extraction_handler = EmotionExtractionHandler()
                emotions = emotion_extraction_handler.emotion_extraction(text)
            # TODO: Change this to Twitter API
            elif model in other_models:
                emotions = []
                for message in text:
                    emotions.append({'text': message, 'emotion': model})
            else:
                return "Model not found", 404

            api_feature_extraction = APIFeatureExtraction()
            features = api_feature_extraction.extract_features(text)

            results = {}
            for review in emotions:
                id_text = review['text']['id']
                results[id_text] = {
                    "emotion": review['emotion'],
                    "text": review['text']
                }

            for review in features:
                id_text = review['id']
                if id_text in results:
                    results[id_text]['features'] = review['features']

            results = list(results.values())

            return jsonify(results)

        except Exception as e:
            return f"An error occurred: {e}"

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host='0.0.0.0', port=3000)