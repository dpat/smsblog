"""Routes for modifying the NUMBER table."""

import logging
import argparse
from flask import Flask, jsonify, request, make_response, Blueprint
from twilio import twiml
from sqlalchemy import inspect

from ..helpers.bphandler import BPHandler
from ..database import DB
from ..database.utils import add_value, table2dict
from ..database.tables.numbers import Numbers
from ..errors.badrequest import BadRequest
from ..errors.notfound import NotFound


NUMBERS_BP = Blueprint('numbers', __name__)
BPHandler.add_blueprint(NUMBERS_BP)


def handler(command):

    if command[0][0] == '-':
        if command[0][:5] == '-get=':
            number_id = command[0][5:]
            return get_number(number_id)
        if command[0][:8] == '-delete=':
            number_id = command[0][8:]
            return delete_number(number_id)
    else:
        number = command[0]
        team = command[1]
        member = command[2]
        if member == 'false':
            member = False

        return add_number(number, team, member)


def add_number(number, team, member):
    """Add a single number to the database."""

    numbers = {}
    values = {'number': number, 'team': team, 'member': member}
    for field in values.keys():
        if field in inspect(Numbers).mapper.column_attrs:
            numbers[field] = values[field]

    new = Numbers(**numbers)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def get_number(id):
    """Get a single number based on the number id, optionally
       return all numbers if id=all"""

    if id == 'all':
        list_of_numbers = []
        numbers = number.query.all()
        for number in numbers:
            list_of_numbers.append(table2dict(number))
        return make_response(jsonify(list_of_numbers), 200)
    else:
        number_id = int(id)
        number = query_numberid(number_id)
        return make_response(jsonify(table2dict(number)), 200)


def delete_number(id):
    """Drop a number from the database"""

    number_id = int(id)
    number = query_numberid(number_id)
    DB.session.delete(number)

    DB.session.commit()
    message = "number number (" + str(number_id) + ") deleted"
    return make_response(jsonify(message), 204)


def query_numberid(number_id):
    """
    Get a number based on the numberid or raise a BadRequest when not found

    :param number_id: int, primary key for the number.
    :return: Table row representing a number.
    """
    number = Numbers.query.filter_by(numberid=number_id).first()
    if not number:
        raise NotFound('number not found')
        return 'number not found'
    return number

