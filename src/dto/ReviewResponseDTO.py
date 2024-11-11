from typing import List
from src.dto.SentenceDTO import SentenceDTO
from datetime import timedelta

class ReviewResponseDTO:
    def __init__(self, id: str, review: str, sentences: List[SentenceDTO], extraction_time: timedelta):
        self.reviewId = id
        self.review = review
        self.sentences = sentences

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time,
            "reviewId": self.reviewId,
            "review": self.review,
            "sentences": [sentence.to_dict() for sentence in self.sentences]
        }