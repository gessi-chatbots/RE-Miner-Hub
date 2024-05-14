class LanguageModelDTO:
    def __init__(self, modelName: str):
        self.modelName = modelName

    def to_dict(self):
        return {
            "modelName": self.modelName,
        }