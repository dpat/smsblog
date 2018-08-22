"""A Module for the Method Not Allowed error."""

from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

METHOD_NOT_ALLOWED_BP = Blueprint('Method Not Allowed', __name__)
BPHandler.add_blueprint(METHOD_NOT_ALLOWED_BP)


class MethodNotAllowed(APIError):
    """
    An object resembling a Method Not Allowed error.

    This class is subclassed from APIError which is subclassed from Exception.
    """

    def __init__(self, message, **kwargs):
        """
        Create a Method Not Allowed error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 405
        self.error = 'Method Not Allowed'


@METHOD_NOT_ALLOWED_BP.app_errorhandler(MethodNotAllowed)
def handle_message_not_allowed(error):
    """Route for handling raised MethodNotAllowed errors."""
    return make_response(error.to_json(), error.code)


@METHOD_NOT_ALLOWED_BP.app_errorhandler(405)
def handle_405(error):
    """Route for handling abort 405 calls."""
    err = MethodNotAllowed(message=str(error))
    return make_response(err.to_json(), err.code)
