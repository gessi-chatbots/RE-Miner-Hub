from src.dto.FeatureDTO import FeatureDTO
from src.dto.SentimentDTO import SentimentDTO

class SentenceDTO:
    def __init__(self, id: str, sentimentData: SentimentDTO, featureData: FeatureDTO, text: str = None):
        self.id = id
        self.sentimentData = sentimentData
        self.featureData = featureData
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "sentimentData": self.sentimentData.to_dict() if self.sentimentData is not None else None,
            "featureData": self.featureData.to_dict() if self.featureData is not None else None,
            "text": self.text
        }