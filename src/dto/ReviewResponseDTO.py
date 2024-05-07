from typing import List
from src.dto.SentenceDTO import SentenceDTO

class ReviewResponseDTO:
    def __init__(self, id: str, review: str, sentences: List[SentenceDTO]):
        self.reviewId = id
        self.review = review
        self.sentences = sentences

    def to_dict(self):
        return {
            "reviewId": self.reviewId,
            "review": self.review,
            "sentences": [sentence.to_dict() for sentence in self.sentences]
        }