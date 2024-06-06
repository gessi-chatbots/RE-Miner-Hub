from src.dto.LanguageModelDTO import LanguageModelDTO

class SentimentDTO:
    def __init__(self, sentiment: str, languageModel: LanguageModelDTO):
        self.sentiment = sentiment
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "sentiment": self.sentiment,
            "languageModel":self.languageModel.to_dict() if self.languageModel is not None else None,
        }