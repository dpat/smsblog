"""Module for the Base Class APIError."""

from flask import jsonify


class APIError(Exception):
    """
    A class for an APIError.

    This is the base class for all errors created to handle API errors.
    """

    def __init__(self, message, **kwargs):
        """
        Create an APIError.

        :param message: String, Message to send along with the error.
        :param kwargs: Other values to send with the error.
        """
        Exception.__init__(self)
        self.message = message
        if kwargs:
            self.__dict__.update(kwargs)

    def to_json(self):
        """Convert the object into a json dictionary."""
        return jsonify(self.__dict__)
