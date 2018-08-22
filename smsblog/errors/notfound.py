"""Module for handling a Not Found error."""
from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

NOT_FOUND_BP = Blueprint('NotFound', __name__)
BPHandler.add_blueprint(NOT_FOUND_BP)


class NotFound(APIError):
    """Class representing a Not Found error."""

    def __init__(self, message, **kwargs):
        """
        Create a Not Found error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 404
        self.error = 'Page Not Found'


@NOT_FOUND_BP.app_errorhandler(NotFound)
def handle_not_found(error):
    """Route for handling a raised Not Found error."""
    return make_response(error.to_json(), error.code)


@NOT_FOUND_BP.app_errorhandler(404)
def handle_404(error):
    """Route for handling an abort 404 error."""
    not_found = NotFound(message=str(error))
    return make_response(not_found.to_json(), not_found.code)
