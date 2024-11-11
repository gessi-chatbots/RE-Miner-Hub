from datetime import timedelta
from src.dto.LanguageModelDTO import LanguageModelDTO

class SentimentDTO:
    def __init__(self, sentiment: str, languageModel: LanguageModelDTO, extraction_time: timedelta = None):
        self.sentiment = sentiment
        self.languageModel = languageModel
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "sentiment": self.sentiment,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
