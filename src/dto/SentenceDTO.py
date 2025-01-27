from src.dto.FeatureDTO import FeatureDTO
from src.dto.SentimentDTO import SentimentDTO
from src.dto.PolarityDTO import PolarityDTO
from src.dto.TypeDTO import TypeDTO
from src.dto.TopicDTO import TopicDTO
from datetime import timedelta

class SentenceDTO:
    def __init__(self, id: str,
                 sentimentData: SentimentDTO,
                 featureData: FeatureDTO,
                 polarityData: PolarityDTO,
                 typeData: TypeDTO,
                 topicData: TopicDTO,
                 text: str = None,
                 extraction_time: timedelta = None):
        self.extraction_time = extraction_time
        self.id = id
        self.sentimentData = sentimentData
        self.featureData = featureData
        self.polarityData = polarityData
        self.typeData = typeData
        self.topicData = topicData
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "sentimentData": self.sentimentData.to_dict() if self.sentimentData is not None else None,
            "featureData": self.featureData.to_dict() if self.featureData is not None else None,
            "polarityData": self.polarityData.to_dict() if self.polarityData is not None else None,
            "typeData": self.typeData.to_dict() if self.typeData is not None else None,
            "topicData": self.topicData.to_dict() if self.topicData is not None else None,
            "text": self.text,
            "extractionTime": self.extraction_time
        }