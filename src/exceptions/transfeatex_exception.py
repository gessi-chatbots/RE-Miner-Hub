class TransfeatExException(Exception):
    def __init__(self, message: str = "There was an error in TransfeatEx", code: int = 400) -> None:
        super().__init__(message, code)
