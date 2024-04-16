from src.emotion_extraction_service import EmotionExtractionService


class AnalysisService():
    def __init__(self) -> None:
        pass

    def analyzeReviews(sentiment_model, feature_model, review_dto_list):
        analyzed_reviews = []
        for review_dto in review_dto_list:
            for index, sentence in enumerate(review_dto.sentences):
                if sentence.text is not None and sentiment_model != '' and sentiment_model == "GPT-3.5":
                    emotion_extraction_handler = EmotionExtractionService()
                    sentence_sentiment = emotion_extraction_handler.emotion_extraction_aux(sentence.text)
                    if sentence_sentiment is not None:
                        sentiment =  sentence_sentiment["emotion"]
                        sentiment_dto = SentimentDTO(sentiment=sentiment)
                        sentence.sentimentData = sentiment_dto
                elif sentence.text is not None and sentiment_model != '' and sentiment_model in EXPECTED_SENTIMENT_MODELS:
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
        return analyzed_reviews