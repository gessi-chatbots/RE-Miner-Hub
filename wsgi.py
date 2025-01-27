import json
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from src.service.analysis_service import AnalysisService
from src.service.performance_service import PerformanceService
from src.exceptions import api_exceptions
from src.utils import extractReviewDTOsFromJson
import logging
import time

#---------------------------------------------------------------------------
#   Application configs
#---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

#---------------------------------------------------------------------------
#   Logging configs
#---------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


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
@app.errorhandler(api_exceptions.TransfeatExException)
def handle_transfeatex_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)


@app.errorhandler(api_exceptions.RequestFormatException)
def handle_request_format_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)


@app.errorhandler(api_exceptions.RequestException)
def handle_request_exception(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)


@app.errorhandler(500)
def handle_internal_server_error(error):
    logging.error(f"Internal Server Error: {str(error)}", exc_info=True)
    return make_response(jsonify({'message': 'Internal Server Error', 'error': str(error)}), 500)


@app.errorhandler(Exception)
def handle_generic_exception(error):
    logging.error(f"Unhandled Exception: {str(error)}", exc_info=True)
    return make_response(jsonify({'message': 'Internal Server Error', 'error': str(error)}), 500)


#---------------------------------------------------------------------------
#   API
#---------------------------------------------------------------------------

EXPECTED_SENTIMENT_MODELS = ["BERT", "BETO", "GPT-3.5"]
EXPECTED_FEATURE_MODELS = ["transfeatex", "t-frex-bert-base-uncased", "t-frex-bert-large-uncased",
                           "t-frex-roberta-base",
                           "t-frex-roberta-large", "t-frex-xlnet-base-cased", "t-frex-xlnet-large-cased"]
EXPECTED_POLARITY_MODELS = ["SVM", "MLP"]
EXPECTED_TYPE_MODELS = ["BERT", "ROBERTA", "DISTILBERT"]
EXPECTED_TOPIC_MODELS = ["SVM", "MLP"]


def validate_request_args(request_args):
    # Check if at least one model type is present
    model_present = any(model + '_model' in request_args.keys() 
                       for model in ['sentiment', 'feature', 'polarity', 'type', 'topic'])
    if not request_args or not model_present:
        raise api_exceptions.RequestFormatException("At least one model type must be specified.", 400)

    # Validate each model if present
    model_validations = {
        'sentiment_model': EXPECTED_SENTIMENT_MODELS,
        'feature_model': EXPECTED_FEATURE_MODELS,
        'polarity_model': EXPECTED_POLARITY_MODELS,
        'type_model': EXPECTED_TYPE_MODELS,
        'topic_model': EXPECTED_TOPIC_MODELS
    }

    for model_name, valid_values in model_validations.items():
        model_value = request.args.get(model_name)
        if model_value is not None and model_value not in valid_values:
            raise api_exceptions.RequestFormatException(f"Unknown {model_name.replace('_', ' ')}", 400)


def process_request_body(request_body):
    if isinstance(request_body, str):
        try:
            body = json.loads(request_body)
        except json.decoder.JSONDecodeError:
            raise api_exceptions.RequestFormatException("Error in decoding request", 400)
    else:
        body = request_body

    #if isinstance(body, list):
    #    try:
    #        reviews = body[0]['reviews']
    #    except (IndexError, KeyError):
    #        raise api_exceptions.RequestFormatException("Error in extracting reviews from list format", 400)
    #else:
    reviews = body
    return extractReviewDTOsFromJson(reviews_dict=reviews)
#---------------------------------------------------------------------------
#   API health check
#---------------------------------------------------------------------------
@app.route('/ping', methods=['GET'])
def ping():
    logging.info(f"Ping API")
    return make_response(jsonify({'message': 'HUB ok'}), 200)


@app.route('/analyze/performance', methods=['POST'])
def test_performance():
    logging.info("Analyze performance request")
    validate_request_args(request.args)
    review_dto_list = process_request_body(request_body=request.get_json(),
                                                                 version=request.args.get('hub_version'))
    performance_service = PerformanceService()
    performance_results = performance_service.test_performance_analysis_reviews(
        version=request.args.get('hub_version', 'v0'),
        sentiment_model=request.args.get("sentiment_model"),
        feature_model=request.args.get("feature_model"),
        review_dto_list=review_dto_list)
    return make_response(performance_results, 200)


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        logging.info("Analyze request")
        validate_request_args(request.args)

        multiprocess = request.args.get("multiprocess", "false").lower() == "true"
        sentiment_model = request.args.get("sentiment_model", None)
        feature_model = request.args.get("feature_model", None)
        polarity_model = request.args.get("polarity_model", None)
        type_model = request.args.get("type_model", None)
        topic_model = request.args.get("topic_model", None)

        review_dto_list = process_request_body(request_body=request.get_json())
        analysis_service = AnalysisService()
        starting_time = time.time()
        if multiprocess:
            analyzed_reviews = analysis_service.analyze_review_sentences_multiprocess(
                sentiment_model=sentiment_model,
                feature_model=feature_model,
                polarity_model=polarity_model,
                type_model=type_model,
                topic_model=topic_model,
                sentences=review_dto_list
            )
        else:
            analyzed_reviews = analysis_service.analyze_reviews(
                sentiment_model=sentiment_model,
                feature_model=feature_model,
                polarity_model=polarity_model,
                type_model=type_model,
                topic_model=topic_model,
                review_dto_list=review_dto_list
            )

        end_time = time.time()
        logging.info(f"Execution time = {end_time - starting_time}s")

        return make_response(jsonify({
            "analyzed_reviews": analyzed_reviews,
            "multiprocess": multiprocess,
            "execution_time": (end_time - starting_time)
        }), 200)
    except Exception as e:
        logging.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        raise


@app.route('/analyze/kg', methods=['POST'])
def analyzeKG():
    logging.info("Analyze request")
    validate_request_args(request.args)
    starting_time = time.time()
    review_dto_list = validate_and_extract_dto_from_request_body(request_body=request.get_json(), version=None)
    end_time = time.time()
    analysis_service = AnalysisService()
    analyzed_reviews = analysis_service.analyze_reviews_kg(
        feature_model=request.args.get("feature_model"),
        review_dto_list=review_dto_list)
    extraction_time = (end_time - starting_time)
    return make_response(
        jsonify({
            "analyzed_reviews": analyzed_reviews,
            "extraction_time": extraction_time,
            "execution_time": (end_time - starting_time)
        }),
        200
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
