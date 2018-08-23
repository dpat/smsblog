import argparse
import logging
from logging import handlers
import os
import shlex

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from .database import DB
from .database.utils import create_tables
from .errors import badrequest, forbidden, gone, internalservererror, \
    methodnotallowed, notfound, unauthorized
from .helpers.bphandler import BPHandler
from .helpers.security import gen_token, list_token, verify_request
from .routes import blog, personal, random, reminder

app = Flask(__name__)


@app.route('/sms', methods=['POST'])
def sms_handler():

    # confirm request is coming from twilio or front end
    verify_request(request, app)

    message_body = str(request.form['Body'])
    args = shlex.split(message_body)
    resp = MessagingResponse()

    if args[0].lower() == 'blog':
        resp.message = blog.handler(args[1:])
    elif args[0].lower() == 'personal':
        resp.message = personal.handler(args[1:])
    elif args[0].lower() == 'reminder':
        resp.message = reminder.handler(args[1:])
    elif args[0].lower() == 'random':
        resp.message = random.handler(args[1:])
    else:
        resp.message = random.collector(args)

    resp.message("this is a test")
    return str(resp)


def config_dabase(app):
    """
    Handle database configuration.

    Create the database directory, set the database path and add the database
    to the Flask app.
    :param app: configured Flask object.
    :return: None
    """
    app_path = '/opt/smsblog'
    if not os.path.exists(app_path):
        os.mkdir(app_path)
    db_path = 'sqlite:///%s/smsblog.db' % app_path
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.app = app
    DB.init_app(app)


def setup_logging(debug=False, verbose=False):
    """
    Configure logging for the application.

    :param debug: Boolean, True will set log level to debug
    :param verbose: Boolean, True will set log level to info
    :return: None
    """
    logger = logging.getLogger()
    log_dir = '/opt/smsblog'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_name = os.path.join(log_dir, 'smsblog.log')
    logger.setLevel(logging.WARNING)
    if debug:
        logger.setLevel(logging.DEBUG)
    elif verbose:
        logger.setLevel(logging.INFO)
    fmt = '%(asctime)s - %(name)s %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt)

    term_channel = logging.StreamHandler()
    term_channel.setFormatter(formatter)
    logger.addHandler(term_channel)

    file_channel = handlers.RotatingFileHandler(file_name,
                                                maxBytes=4000000,
                                                backupCount=8)
    logger.addHandler(file_channel)


def launch_api():
    """Parse the arguments and launch the desired command."""
    parser = argparse.ArgumentParser(description='Launch a API with routes '
                                                 'for a test application')
    parser.add_argument('-d', '--debug',
                        help='turn on the debug flag',
                        default=False,
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='turn on terminal output',
                        default=False,
                        action='store_true')
    subparser = parser.add_subparsers(dest='subcmd')
    subparser.required = True

    subparser.add_parser('init', help='setup the database')

    run = subparser.add_parser('run', help='run the app')

    run.add_argument('-p', '--port',
                     help='port to run the app on',
                     type=int,
                     default=None)
    run.add_argument('-u', '--url',
                     help='public url of site',
                     default=None)
    run.add_argument('-a', '--auth',
                     help='twilio authentication token',
                     default=None)
    token = subparser.add_parser('token', help='generate a fresh token')
    token.add_argument('-l', '--list',
                       help='List all current tokens',
                       default=False,
                       action='store_true')

    args = parser.parse_args()
    cmd = vars(args).pop('subcmd')
    setup_logging(args.debug, args.verbose)
    BPHandler.register_blueprints(app)
    config_dabase(app)

    if cmd == 'run':
        app.config['site_url'] = args.url
        app.config['auth_token'] = args.auth
        app.run(debug=args.debug, port=args.port)
    elif cmd == 'init':
        create_tables()
    elif cmd == 'token':
        if args.list:
            list_token()
        else:
            gen_token()
