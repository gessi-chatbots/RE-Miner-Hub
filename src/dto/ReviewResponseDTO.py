from typing import List, Optional
from src.dto.SentenceDTO import SentenceDTO
from datetime import timedelta

class ReviewResponseDTO:
    def __init__(self, id: str, review: str, sentences: List[SentenceDTO], extraction_time: Optional[timedelta] = None):
        self.reviewId = id
        self.review = review
        self.sentences = sentences
        self.extraction_time = extraction_time

    def to_dict(self):
        return {
            "extractionTime": self.extraction_time.total_seconds() if self.extraction_time else None,
            "reviewId": self.reviewId,
            "review": self.review,
            "sentences": [sentence.to_dict() for sentence in self.sentences]
        }
