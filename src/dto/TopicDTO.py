from datetime import timedelta
from src.dto.LanguageModelDTO import LanguageModelDTO

class TopicDTO:
    def __init__(self, topic: str, languageModel: LanguageModelDTO, extraction_time: timedelta = None):
        self.topic = topic
        self.languageModel = languageModel
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "topic": self.topic,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
