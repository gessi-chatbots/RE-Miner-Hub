from src.dto.LanguageModelDTO import LanguageModelDTO

class FeatureDTO:
    def __init__(self, feature: str, languageModel: LanguageModelDTO):
        self.feature = feature
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "feature": self.feature,
            "languageModel":self.languageModel.to_dict() if self.languageModel is not None else None,
        }