class TransfeatExException(Exception):
    code = 500
    message = "There was an error in TransfeatEx"

class RequestException(Exception):
    code = 500
    message = "There was a request error"

class RequestFormatException(Exception):
    code = 500
    message = "Wrong request format"
