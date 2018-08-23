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


def handler(command):

    if command[0][0] == '-':
        if command[0][:5] == '-get=':
            reminder_id = command[6:]
            get_reminder(reminder_id)
        if command[0][:8] == '-delete=':
            reminder_id = command[9:]
            delete_reminder(reminder_id)
    else:
        days = command[0]
        time = command[1]
        if command[2][:3] == '-r=':
            recurring = command[2][4:]
            message = command[3:]
        else:
            recurring = 'once'
            message = command[2:]

        add_reminder(days, time, recurring, message)


def add_reminder(days, time, recurring, message):
    """Add a single reminder to the database."""

    reminder = {}
    values = {'days': days, 'time': time, 'recurring': recurring,
              'message': message}

    for field in values.keys():
        if field in inspect(Reminder).mapper.column_attrs:
            reminder[field] = values[field]

    new = Reminder(**reminder)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def get_reminder(id):
    """Get a single reminder based on the reminder id, optionally
       return all reminders if id=all"""

    if id == 'all':
        list_of_reminders = []
        reminders = Reminder.query.all()
        for reminder in reminders:
            list_of_reminders.append(table2dict(reminder))
        return make_response(jsonify(list_of_reminders), 200)
    else:
        reminder_id = int(id)
        reminder = query_reminderid(reminder_id)
        return make_response(jsonify(table2dict(reminder)), 200)


def delete_reminder(id):
    """Drop a reminder from the database"""

    reminder = query_reminderid(id)
    reminder.delete()

    DB.session.commit()
    return make_response('', 204)


def query_reminderid(reminder_id):
    """
    Get a reminder based on the reminderid or raise a BadRequest when not found

    :param post_id: int, primary key for the post.
    :return: Table row representing a post.
    """
    reminder = Reminder.query.filter_by(reminderid=reminder_id).first()
    if not reminder:
        raise NotFound('Reminder not found')
        return 'Reminder not found'
    return reminder
