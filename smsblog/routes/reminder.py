"""Routes for modifying the Reminder table."""

import logging
import argparse
from flask import Flask, jsonify, request, make_response, Blueprint
from twilio import twiml
from sqlalchemy import inspect

from ..helpers.bphandler import BPHandler
from ..database import DB
from ..database.utils import add_value, table2dict
from ..database.tables.reminder import Reminder
from ..errors.badrequest import BadRequest
from ..errors.notfound import NotFound


REMINDER_BP = Blueprint('reminder', __name__)
BPHandler.add_blueprint(REMINDER_BP)


def reminder_handler(command):
    parser = argparse.ArgumentParser(description='Parse reminder args')

    parser.add_argument('-r', '-recurring',
                        nargs=1,
                        help='interval of time to send reminder',
                        action='store_true')
    parser.add_argument('days',
                        nargs=1,
                        help='# of days from setting to send reminder',
                        action='store_true',
                        required=True)
    parser.add_argument('time',
                        nargs=1,
                        help='time to send reminder',
                        action='store_true',
                        required=True)
    parser.add_argument('reminder',
                        help='the body of the reminder',
                        nargs='+',
                        default='N/A',
                        action='store_true')

    subparser = parser.add_subparsers(dest='subcmd')

    recurring = subparser.add_parser('recurring', help='set recurring reminder')
    recurring.add_argument('recurring',
                           nargs=1,
                           help='interval of time to send reminder',
                           action='store_true')
    recurring.add_argument('days',
                           nargs=1,
                           help='# of days from setting to send reminder',
                           action='store_true',
                           required=True)
    recurring.add_argument('time',
                           nargs=1,
                           help='time to send reminder',
                           action='store_true',
                           required=True)
    recurring.add_argument('reminder',
                           help='the body of the reminder',
                           nargs='+',
                           default='N/A',
                           action='store_true')

    today = subparser.add_parser('today', help='set a reminder for today')
    today.add_argument('-r', '-recurring',
                       nargs=1,
                       help='interval of time to send reminder',
                       action='store_true')
    today.add_argument('time',
                       nargs=1,
                       help='time to send reminder',
                       action='store_true',
                       required=True)
    today.add_argument('reminder',
                       help='the body of the reminder',
                       nargs='+',
                       default='N/A',
                       action='store_true')

    a = subparser.add_parser('a', help='sets a reminder for 24 hours later')
    a.add_argument('-r', '-recurring',
                   nargs=1,
                   help='interval of time to send reminder',
                   action='store_true')
    a.add_argument('reminder',
                   help='the body of the reminder',
                   nargs='+',
                   default='N/A',
                   action='store_true')

    get = subparser.add_parser('get', help='get a reminder')
    get.add_argument('id',
                     help='id of reminder',
                     Required=True)

    delete = subparser.add_parser('delete', help='delete a reminder')
    delete.add_argument('id',
                        help='id of reminder',
                        Required=True)

    args = parser.parse_args(command)
    cmd = vars(args).pop('subcmd')

    if not cmd:
        basic_reminder(args)
    elif cmd == 'recurring':
        recurring_reminder(args)
    elif cmd == 'today':
        today_reminder(args)
    elif cmd == 'a':
        a_reminder(args)
    elif cmd == 'delete':
        delete_reminder(args)
    else:
        return 'failed'


def add_reminder(args, days, time):
    reminder = ' '.join(args.reminder)
    values = {'days': days, 'time': time, 'reminder': reminder}
    if args.recurring:
        recurring = str(args.recurring)
        values['recurring'] = recurring
    for field in values.keys():
        if field in inspect(Reminder).mapper.column_attrs:
            reminder[field] = values[field]

    new = Reminder(**reminder)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def basic_reminder(args):
    """Add a single reminder to the database."""

    days = args.days
    time = args.time
    return add_reminder(args, days, time)


def recurring_reminder(args):
    """Add a single recurring reminder to the database."""

    days = args.days
    time = args.time
    return add_reminder(args, days, time)


def today_reminder(args):
    """Add a single reminder to the database."""

    days = 0
    time = args.time
    return add_reminder(args, days, time)


def a_reminder(args):
    """Add a single reminder to the database."""

    days = 0
    time = 2400
    return add_reminder(args, days, time)


def get_reminder(args):
    """Get a single reminder based on the reminder id, optionally
       return all reminders if id=all"""

    if args.id == 'all':
        list_of_reminders = []
        reminders = Reminder.query.all()
        for reminder in reminders:
            list_of_reminders.append(table2dict(reminder))
        return make_response(jsonify(list_of_reminders), 200)
    else:
        reminder_id = int(args.id)
        reminder = query_reminderid(reminder_id)
        return make_response(jsonify(table2dict(reminder)), 200)


def delete_reminder(args):
    """Drop a reminder from the database"""

    reminder = query_reminderid(args.id)
    reminder.delete()

    DB.session.commit()
    return make_response('', 204)


def query_reminderid(reminder_id):
    """
    Get a reminder based on the reminderid or raise a BadRequest when not found.

    :param post_id: int, primary key for the post.
    :return: Table row representing a post.
    """
    reminder = Reminder.query.filter_by(reminderid=reminder_id).first()
    if not reminder:
        raise NotFound('Reminder not found')
        return 'Reminder not found'
    return reminder
