class FeatureDTO:
    def __init__(self, feature: str):
        self.feature = feature

    def to_dict(self):
        return {
            "feature": self.feature,
        }