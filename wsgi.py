import json
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from service.analysis_service import AnalysisService
from exceptions import api_exceptions
from utils import extractReviewDTOsFromJson
import logging

#---------------------------------------------------------------------------
#   Application configs
#---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

#---------------------------------------------------------------------------
#   Logging configs
#---------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#---------------------------------------------------------------------------
#   Flask Swagger configs
#---------------------------------------------------------------------------
@app.route('/swagger.yaml')
def swagger_yaml():
    return send_file('swagger.yaml')

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

#---------------------------------------------------------------------------
#   Exception Handlers
#---------------------------------------------------------------------------
@app.handle_exception(api_exceptions.TransfeatExException)
def handle_transfeatex_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

@app.handle_exception(api_exceptions.RequestException)
def handle_request_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

@app.handle_exception(api_exceptions.RequestException)
def handle_request_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

#---------------------------------------------------------------------------
#   API
#---------------------------------------------------------------------------

EXPECTED_SENTIMENT_MODELS = ["BERT", "BETO", "GPT-3.5"]
EXPECTED_FEATURE_MODELS = ["transfeatex", "t-frex-bert-base-uncased", "t-frex-bert-large-uncased", "t-frex-roberta-base",
                                 "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]

def validate_request_args(request_args):
    if not request_args \
            or ('sentiment_model' not in request_args.keys() and 'feature_model' not in request_args.keys()) \
            and 'text' not in request.json.keys():
        raise api_exceptions.RequestFormatException("Lacking model and textual data in proper tag.", 400)
    if 'sentiment_model' not in request_args.keys() and 'feature_model' not in request_args.keys():
        raise api_exceptions.RequestFormatException("Lacking model in proper tag.", 400)
    if request.args.get("sentiment_model") is not None and request.args.get("sentiment_model") not in EXPECTED_SENTIMENT_MODELS:
        raise api_exceptions.RequestFormatException("Unknown sentiment model", 400)
    if request.args.get("feature_model") is not None and request.args.get("feature_model") not in EXPECTED_FEATURE_MODELS:
        raise api_exceptions.RequestFormatException("Unknown feature model", 400)

def validate_and_extract_dto_from_request_body(request_body):
    if request_body is None:
        raise api_exceptions.RequestFormatException("No reviews submitted for analysis", 400)
 
    if isinstance(request_body, str):
        try:
            reviews_json = json.loads(request_body)
        except json.decoder.JSONDecodeError:
            raise api_exceptions.RequestFormatException("Error in decoding request", 400)
    else:
        reviews_json = request_body

    return extractReviewDTOsFromJson(reviews_json)

@app.route('/analyze', methods=['POST'])
def analyze():
    validate_request_args(request.args)
    review_dto_list = validate_and_extract_dto_from_request_body(request_body=request.get_json)
    analysis_service = AnalysisService()
    analyzed_reviews = analysis_service.analyze_reviews(sentiment_model = request.args.get("sentiment_model"), 
                                                       feature_model= request.args.get("feature_model"), 
                                                       review_dto_list= review_dto_list)
    return make_response(analyzed_reviews, 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
