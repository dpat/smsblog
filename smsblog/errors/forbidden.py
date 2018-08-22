"""Module for a Forbidden error."""
from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

FORBIDDEN_BP = Blueprint('Forbidden', __name__)
BPHandler.add_blueprint(FORBIDDEN_BP)


class Forbidden(APIError):
    """Class representing a Forbidden error."""

    def __init__(self, message, **kwargs):
        """
        Create a Forbidden error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 403
        self.error = 'Forbidden'


@FORBIDDEN_BP.app_errorhandler(Forbidden)
def handle_forbidden(error):
    """Route for handling raised Forbidden errors."""
    return make_response(error.to_json(), error.code)


@FORBIDDEN_BP.app_errorhandler(403)
def handle_403(error):
    """Route for handling abort 403."""
    forbidden = Forbidden(message=str(error))
    return make_response(forbidden.to_json(), forbidden.code)
