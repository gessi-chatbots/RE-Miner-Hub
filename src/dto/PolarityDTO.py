from datetime import timedelta
from src.dto.LanguageModelDTO import LanguageModelDTO

class PolarityDTO:
    def __init__(self, polarity: str, languageModel: LanguageModelDTO, extraction_time: timedelta = None):
        self.polarity = polarity
        self.languageModel = languageModel
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "polarity": self.polarity,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
