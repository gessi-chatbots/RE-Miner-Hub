from src.dto.LanguageModelDTO import LanguageModelDTO
from datetime import timedelta

class FeatureDTO:
    def __init__(self, feature: str, languageModel: LanguageModelDTO, extraction_time: timedelta = None):
        self.feature = feature
        self.languageModel = languageModel
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "feature": self.feature,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
