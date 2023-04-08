import requests


class IpswException(Exception):
    """
    A base class from which all other exceptions inherit.
    If you want to catch all errors that the ipsw SDK might raise,
    catch this base exception.
    """


def create_api_error_from_http_exception(e):
    """
    Create a suitable APIError from requests.exceptions.HTTPError.
    """
    response = e.response
    try:
        explanation = response.json()["message"]
    except ValueError:
        explanation = (response.content or "").strip()
    cls = APIError
    if response.status_code == 404:
        cls = NotFound
    raise cls(e, response=response, explanation=explanation) from e


class APIError(requests.exceptions.HTTPError, IpswException):
    """
    An HTTP error from the API.
    """

    def __init__(self, message, response=None, explanation=None):
        # requests 1.2 supports response as a keyword argument, but
        # requests 1.1 doesn't
        super().__init__(message)
        self.response = response
        self.explanation = explanation

    def __str__(self):
        message = super().__str__()

        if self.is_client_error():
            message = "{} Client Error for {}: {}".format(
                self.response.status_code, self.response.url, self.response.reason
            )

        elif self.is_server_error():
            message = "{} Server Error for {}: {}".format(
                self.response.status_code, self.response.url, self.response.reason
            )

        if self.explanation:
            message = f'{message} ("{self.explanation}")'

        return message

    @property
    def status_code(self):
        if self.response is not None:
            return self.response.status_code

    def is_error(self):
        return self.is_client_error() or self.is_server_error()

    def is_client_error(self):
        if self.status_code is None:
            return False
        return 400 <= self.status_code < 500

    def is_server_error(self):
        if self.status_code is None:
            return False
        return 500 <= self.status_code < 600


class NotFound(APIError):
    pass

class InvalidVersion(IpswException):
    pass


class StreamParseError(RuntimeError):
    def __init__(self, reason):
        self.msg = reason
