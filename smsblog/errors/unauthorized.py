"""Module for handling an Unauthorized error."""

from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

UNAUTHORIZED_BP = Blueprint('Unauthorized', __name__)
BPHandler.add_blueprint(UNAUTHORIZED_BP)


class Unauthorized(APIError):
    """
    Class for an Unauthorized error.

    Is subclassed from APIError which is subclassed from Exception.
    """

    def __init__(self, message, **kwargs):
        """
        Create an Internal Server Error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 401
        self.error = 'Unauthorized'


@UNAUTHORIZED_BP.app_errorhandler(Unauthorized)
def handle_unauthorized(error):
    """Route for handling an Unauthorized error."""
    return make_response(error.to_json(), error.code)
