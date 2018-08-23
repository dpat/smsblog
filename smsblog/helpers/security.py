import logging
import random
import string
import collections


from ..database import DB
from ..database.tables.token import Token
from ..errors.forbidden import Forbidden
from ..errors.unauthorized import Unauthorized
from twilio.request_validator import RequestValidator


def gen_token(length=40):
    """
    Create a new token used to verify a user has write permission.

    Once the new token is generated, it is saved to the database.

    :param length: Integer, length of a token to generate
    :return: None
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    token = ''
    logger.debug('Generating new token length %s', length)
    for i in range(length):
        token += random.choice(string.ascii_letters + string.digits)
    this = Token(token=token)
    DB.session.add(this)
    DB.session.commit()
    logger.info('created token')
    logger.info(token)
    return token


def list_token():
    """
    List all current tokens in the database.

    :return: None
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    result = Token.query.all()
    for token in result:
        logger.info(token.token)


def check_token(token):
    """
    Check if a token exists in the database.

    :param token: String, a string of characters used as an API token
    :return: Boolean, true if the api token exists in the database
    """
    result = Token.query.filter_by(token=token).first()
    if result:
        return True
    raise Unauthorized('Bad API token')
    return False


def get_token(request):
    """
    Get an API token from a flask.request object.

    :param request: flask.request: a request from a http(s) request
    :return: String, token used ot authenticate api requests
    """
    token = request.headers.get('Token')
    if not token:
        return False
    return token


def verify_twilio(request, app):

    # use twilio's docs on validating a request
    url = app.config.get('site_url')
    auth_token = app.config.get('auth_token')
    params = request.form
    validator = RequestValidator(auth_token)
    tw_sig = request.headers.get('X-Twilio-Signature')
    return(validator.validate(url, params, tw_sig))


def verify_request(request, app):
    token = get_token(request)
    if token is False:
        return False
    elif check_token(token):
        return True
    else:
        return False
