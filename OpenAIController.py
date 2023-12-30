import flask
from flask import Flask, request, jsonify

from src.emotion_extraction_handler import EmotionExtractionHandler

def create_app():
    app = Flask(__name__)

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