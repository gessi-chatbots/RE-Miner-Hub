from datetime import timedelta
from src.dto.LanguageModelDTO import LanguageModelDTO

class TypeDTO:
    def __init__(self, type: str, languageModel: LanguageModelDTO, extraction_time: timedelta = None):
        self.type = type
        self.languageModel = languageModel
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "type": self.type,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
