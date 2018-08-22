"""Module for handling a Bad Request error."""

from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler


BAD_REQUEST_BP = Blueprint('BadRequest', __name__)
BPHandler.add_blueprint(BAD_REQUEST_BP)


class BadRequest(APIError):
    """Class representing a Bad Request."""

    def __init__(self, message, **kwargs):
        """
        Create a Bad Request error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 400
        self.error = 'Bad Request'


@BAD_REQUEST_BP.app_errorhandler(BadRequest)
def handle_bad_request(error):
    """Route for handling raised Bad Requests."""
    return make_response(error.to_json(), error.code)
