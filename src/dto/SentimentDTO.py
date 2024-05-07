class SentimentDTO:
    def __init__(self, sentiment: str):
        self.sentiment = sentiment

    def to_dict(self):
        return {
            "sentiment": self.sentiment,
        }