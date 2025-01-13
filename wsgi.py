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
    if not request_args \
            or ('sentiment_model' not in request_args.keys() and 'feature_model' not in request_args.keys()):
        raise api_exceptions.RequestFormatException("Lacking model and textual data in proper tag.", 400)
    if 'sentiment_model' not in request_args.keys() and 'feature_model' not in request_args.keys():
        raise api_exceptions.RequestFormatException("Lacking model in proper tag.", 400)
    if request.args.get("sentiment_model") is not None and request.args.get(
            "sentiment_model") not in EXPECTED_SENTIMENT_MODELS:
        raise api_exceptions.RequestFormatException("Unknown sentiment model", 400)
    if request.args.get("feature_model") is not None and request.args.get(
            "feature_model") not in EXPECTED_FEATURE_MODELS:
        raise api_exceptions.RequestFormatException("Unknown feature model", 400)
    if request.args.get("polarity_model") is not None and request.args.get(
            "polarity_model") not in EXPECTED_POLARITY_MODELS:
        raise api_exceptions.RequestFormatException("Unknown polarity model", 400)
    if request.args.get("type_model") is not None and request.args.get(
            "type_model") not in EXPECTED_TYPE_MODELS:
        raise api_exceptions.RequestFormatException("Unknown type model", 400)
    if request.args.get("topic_model") is not None and request.args.get(
            "topic_model") not in EXPECTED_TOPIC_MODELS:
        raise api_exceptions.RequestFormatException("Unknown topic model", 400)



def process_request_body(request_body):
    if isinstance(request_body, str):
        try:
            body = json.loads(request_body)
        except json.decoder.JSONDecodeError:
            raise api_exceptions.RequestFormatException("Error in decoding request", 400)
    else:
        body = request_body

    if isinstance(body, list):
        try:
            reviews = body[0]['reviews']
        except (IndexError, KeyError):
            raise api_exceptions.RequestFormatException("Error in extracting reviews from list format", 400)
    else:
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
