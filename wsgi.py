import json
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from src.service.analysis_service import AnalysisService
from src.service.performance_service import PerformanceService
from src.exceptions import api_exceptions
from src.utils import extractReviewDTOsFromJson, extractReviewDTOsFromJsonAux
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
            # Check the shape of the first review to determine which function to use
            first_review = body[0]
            if 'applicationId' in first_review and 'date' in first_review:
                # Use Aux function for this shape
                return extractReviewDTOsFromJsonAux(reviews_dict=body)
            elif 'reviewId' in first_review and 'review' in first_review:
                # Use the main function for this shape
                return extractReviewDTOsFromJson(reviews_dict=body)
            else:
                raise api_exceptions.RequestFormatException("Unexpected review format", 400)
        except (IndexError, KeyError):
            raise api_exceptions.RequestFormatException("Error in extracting reviews from list format", 400)
    else:
        raise api_exceptions.RequestFormatException("Unsupported request format", 400)

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

    sentiment_model = request.args.get("sentiment_model", None)
    feature_model = request.args.get("feature_model", None)

    sibling_threshold = request.args.get("sibling_threshold", None)
    if sibling_threshold is not None:
        try:
            sibling_threshold = float(sibling_threshold)
        except ValueError:
            return make_response(jsonify({"error": "Invalid sibling_threshold value"}), 400)

    review_dto_list = process_request_body(request_body=request.get_json())
    app_name = request.get_json()[0].get('applicationId')
    analysis_service = AnalysisService()
    analysis_starting_time = time.time()

    analyzed_reviews = analysis_service.analyze_reviews(
        sentiment_model=sentiment_model,
        feature_model=feature_model,
        review_dto_list=review_dto_list,
    )

    analysis_ending_time = time.time()
    logging.info(f"Execution time = {analysis_ending_time - analysis_starting_time}s")
    clustering_starting_time = time.time()

    analysis_service.clusterize_reviews(app_name, analyzed_reviews, sibling_threshold)
    clustering_ending_time = time.time()
    logging.info(f"Clustering time = {clustering_ending_time - clustering_starting_time}s")


    return make_response(jsonify({
        "analyzed_reviews": analyzed_reviews,
        "execution_time": (analysis_ending_time - analysis_starting_time),
        "clustering_time": (clustering_ending_time - clustering_starting_time),
        "sibling_threshold": sibling_threshold
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
