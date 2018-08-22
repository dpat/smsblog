"""Module for handling a Gone error."""

from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

GONE_BP = Blueprint('Gone', __name__)
BPHandler.add_blueprint(GONE_BP)


class Gone(APIError):
    """Class representing a Gone error."""

    def __init__(self, message, **kwargs):
        """
        Create a Bad Request error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 410
        self.error = 'Gone'


@GONE_BP.app_errorhandler(Gone)
def handle_gone(error):
    """Route for handling a raised Gone error."""
    return make_response(error.to_json(), error.code)


@GONE_BP.app_errorhandler(410)
def handle_410(error):
    """Route for handling an abort 410."""
    gone = Gone(message=str(error))
    return make_response(gone.to_json(), gone.code)
