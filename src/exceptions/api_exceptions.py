class TransfeatExException(Exception):
    def __init__(self, message: str = "There was an error in TransfeatEx", code: int = 400) -> None:
        super().__init__(message, code)

class RequestException(Exception):
    def __init__(self, message: str = "There was a request error", code: int = 500) -> None:
        super().__init__(message, code)

class RequestFormatException(Exception):
    def __init__(self, message: str ="Wrong request format", code: int = 400) -> None:
        super().__init__(message, code)