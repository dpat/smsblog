import argparse
import logging
from logging import handlers
import os
import json
import base64
import requests
import datetime
from twilio.rest import Client

ACCOUNT_SID = 'ACece666d4e0527c050070a6635e0355dc'
AUTH_TOKEN = '620c522b5424afa689328196ffceb3c9'
NOTIFY_SERVICE_SID = 'ISb17d4f8b7da6914ac19c89b85fa1ea7e'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

from flask import Flask, request, make_response, jsonify
from twilio.twiml.messaging_response import MessagingResponse, Message
from .database import DB
from .database.utils import create_tables
from .errors import badrequest, forbidden, gone, internalservererror, \
                    methodnotallowed, notfound, unauthorized
from .helpers.reminder_utils import initiate_reminders
from .helpers.bphandler import BPHandler
from .helpers.formatting import response_string, request_sms_args, \
                                request_api_args
from .helpers.security import gen_token, list_token, verify_request, \
                              verify_twilio
from .routes import blog, personal, random, reminder, numbers

app = Flask(__name__)


def return_app():
        return app


@app.route('/', methods=['GET'])
def home():
        return('home')


def get_day_score(date):
    apikey = '7240a951-22c7-4a0c-b816-ef4ef6'
    try:
        response = requests.get(

            url='https://api.mysportsfeeds.com/v2.1/pull/nba/current/date/{0}/games.json?status=final'.format(date),
            params={
                "fordate": date
            },
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(apikey,'MYSPORTSFEEDS').encode('utf-8')).decode('ascii')
            }
        )

        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
    jsonVals = json.loads(response.text)
    games = jsonVals['games']
    scores = []
    for game in games:
        score = {}
        score['away'] = {}
        score['home'] = {}
        score['away']['team'] = game['schedule']['awayTeam']['abbreviation']
        score['home']['team'] = game['schedule']['homeTeam']['abbreviation']
        score['away']['score'] = game['score']["awayScoreTotal"]
        score['home']['score'] = game['score']["homeScoreTotal"]
        scores.append(score)
    smsString = ''
    for score in scores:
        awayScore = score['away']['score']
        homeScore = score['home']['score']
        awayTeam = score['away']['team']
        homeTeam = score['home']['team']
        if homeScore > awayScore:
            winningTeam = homeTeam
            winningScore = homeScore
            losingScore = awayScore
        elif homeScore < awayScore:
            winningTeam = awayTeam
            winningScore = awayScore
            losingScore = homeScore
        else:
            winningTeam = ''
            winningScore = homeScore
            losingScore = homeScore

        smsString = smsString + ('{0} at {1}, final {2}-{3} {4}'.format(awayTeam, homeTeam, winningScore, losingScore, winningTeam))
    return smsString

@app.route('/sms', methods=['POST'])
def sms_handler():


    resp = MessagingResponse()
    num = str(request.form['From'])

    # confirm request is coming from twilio
    if not verify_twilio(request, app):
        resp.message("unverified twilio request has been sent")
        return str(resp)
        smsString = get_day_score('20200819')
        responseScore = make_response(jsonify(smsString), 201)
        resp.message(response_string(responseScore))

    # confirm request is coming from correct phone line
    if not num == app.config.get('num'):
        resp.message("unverified twilio number has been used")
        return str(resp)

    args = request_sms_args(request)

    if args[0].lower() == 'blog':
        resp.message(response_string(blog.handler(args[1:])))
    elif args[0].lower() == 'personal':
        resp.message(response_string(personal.handler(args[1:])))
    elif args[0].lower() == 'reminder':
        resp.message(response_string(reminder.handler(args[1:])))
    elif args[0].lower() == 'random':
        resp.message(response_string(random.handler(args[1:])))
    else:
        resp.message(response_string(random.collector(args)))

    return str(resp)


@app.route('/api', methods=['POST'])
def api_handler():

    # confirm request is coming from correct program
    if not verify_request(request, app):
        return False

    args = request_api_args(request)

    if args[0].lower() == 'blog':
        return blog.handler(args[1:])
    elif args[0].lower() == 'personal':
        return personal.handler(args[1:])
    elif args[0].lower() == 'reminder':
        return reminder.handler(args[1:])
    elif args[0].lower() == 'random':
        return random.handler(args[1:])
    elif args[0].lower() == 'daily_scores':
        return send_bulk_sms()
    else:
        return send_bulk_sms()
	#numbers.handler(args)

def send_bulk_sms():
    prevday = datetime.datetime.today()-datetime.timedelta(1)
    date = prevday.strftime('%Y%m%d')
    body = get_day_score(date)
    #return 'this is a string'
    #bindings = "{'binding_type':'sms','address':'+15173031634'}"
    binding = client.notify.services(NOTIFY_SERVICE_SID).bindings.create(
        # We recommend using a GUID or other anonymized identifier for Identity
        identity='00000001',
        binding_type='sms',
        address='+15173031634')
    notification = client.notify.services(NOTIFY_SERVICE_SID).notifications.create(
        #to_binding=["{'binding_type':'sms','address':'+15173031634'}"],
        identity='00000001',
        body='test!'
    )
    return make_response('test', 201)

def config_database(app):
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
    run.add_argument('-n', '--num',
                     help='number of site owner',
                     default=None)
    run.add_argument('-t', '--tnum',
                     help='number for twilio reminder texts',
                     default=None)
    run.add_argument('-u', '--url',
                     help='public url of site',
                     default=None)
    run.add_argument('-a', '--auth',
                     help='twilio authentication token',
                     default=None)
    run.add_argument('-s', '--sid',
                     help='twilio account sid',
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
    config_database(app)

    if cmd == 'run':
        app.config['num'] = args.num
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

