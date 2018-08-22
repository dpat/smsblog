"""Module for handling Internal Server Errors or abort 500."""
from flask import make_response, Blueprint

from .apierror import APIError
from ..helpers.bphandler import BPHandler

INTERNAL_SERVER_ERROR_BP = Blueprint('Internal Server Error', __name__)
BPHandler.add_blueprint(INTERNAL_SERVER_ERROR_BP)


class InternalServerError(APIError):
    """
    Error class representing an Internal Server Error (500).

    Is subclassed from APIError which is subclassed from Exception.
    """

    def __init__(self, message, **kwargs):
        """
        Create an Internal Server Error.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        super().__init__(message, **kwargs)
        self.code = 500
        self.error = 'Internal Server Error'


@INTERNAL_SERVER_ERROR_BP.app_errorhandler(InternalServerError)
def handle_internal_server_error(error):
    """Define a route to handle an Internal Server Error when raised."""
    return make_response(error.to_json(), error.code)


@INTERNAL_SERVER_ERROR_BP.app_errorhandler(500)
def handle_500(error):
    """Define a route to handle an abort 500 error."""
    ise = InternalServerError(message=str(error))
    return make_response(ise.to_json(), ise.code)
