import flask
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from src.emotion_extraction_handler import EmotionExtractionHandler

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

    @app.route('/extract-emotion', methods=['POST'])
    def get_emotion():
        try:
            if 'messages' not in request.json.keys():
                return "Lacking textual data in proper tag.", 400

            emotion_extraction_handler = EmotionExtractionHandler()
            data = request.get_json()
            messages = data.get("messages")

            results = emotion_extraction_handler.emotion_extraction(messages)

            return jsonify(results)

        except Exception as e:
            return f"An error occurred: {e}"

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host='0.0.0.0')