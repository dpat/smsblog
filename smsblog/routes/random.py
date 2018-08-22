"""Routes for modifying the Random table."""

import logging
import argparse
from flask import Flask, jsonify, request, make_response, Blueprint
from twilio import twiml
from sqlalchemy import inspect

from ..helpers.bphandler import BPHandler
from ..database import DB
from ..database.utils import add_value, table2dict
from ..database.tables.random import Random
from ..errors.badrequest import BadRequest
from ..errors.notfound import NotFound


RANDOM_BP = Blueprint('random', __name__)
BPHandler.add_blueprint(RANDOM_BP)


def random_collector(command):
    parser = argparse.ArgumentParser(description='Parse random post args')

    parser.add_argument('-c', '-category',
                        nargs=1,
                        default='random_collector',
                        help='category of random post',
                        action='store_true')
    parser.add_argument('post',
                        help='the body of the random post',
                        nargs='+',
                        default='N/A',
                        action='store_true')

    args = parser.parse_args(command)
    add_post(args)


def random_handler(command):
    parser = argparse.ArgumentParser(description='Parse random post args')

    parser.add_argument('-c', '-category',
                        nargs=1,
                        default='general',
                        help='category of random post',
                        action='store_true')
    parser.add_argument('post',
                        help='the body of the random post',
                        nargs='+',
                        default='N/A',
                        action='store_true')

    subparser = parser.add_subparsers(dest='subcmd')

    get = subparser.add_parser('get', help='get a post')
    get.add_argument('id',
                     help='id of post',
                     Required=True)

    update = subparser.add_parser('update', help='update a post')
    update.add_argument('id_and_post',
                        help='id and updated post',
                        nargs='+',
                        Required=True)
    update.add_argument('-c', '-category',
                        nargs=1,
                        default='N/A',
                        help='category of random post',
                        action='store_true')

    delete = subparser.add_parser('delete', help='delete a post')
    delete.add_argument('id',
                        help='id of post',
                        Required=True)

    args = parser.parse_args(command)
    cmd = vars(args).pop('subcmd')

    if not cmd:
        add_post(args)
    elif cmd == 'get':
        get_post(args)
    elif cmd == 'update':
        update_post(args)
    elif cmd == 'delete':
        delete_post(args)
    else:
        return 'failed'


def add_post(args):
    """Add a single post to the database."""

    post = ' '.join(args.post)
    category = args.category
    values = {'category': category, 'post': post}
    random = {}
    required = ['category', 'post']
    for field in required:
        if field in inspect(Random).mapper.column_attrs:
            random[field] = values[field]

    new = Random(**random)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def get_post(args):
    """Get a single post based on the post id, optionally
       return all posts if id=all"""

    if args.id == 'all':
        list_of_posts = []
        posts = Random.query.all()
        for post in posts:
            list_of_posts.append(table2dict(post))
        return make_response(jsonify(list_of_posts), 200)
    else:
        post_id = int(args.id)
        post = query_postid(post_id)
        return make_response(jsonify(table2dict(post)), 200)


def update_post(args):
    """Update a post based on its post id."""
    category = args.category
    post_id = int(args.id_and_post[0])
    new_post = ' '.join(args.id_and_post[1:])
    old_post = query_postid(post_id)
    values = {'category': category, 'post': new_post}
    for field in values.keys():
        if category == 'N/A':
            continue
        if field in inspect(Random).mapper.column_attrs:
            setattr(old_post, field, values[field])

    DB.session.commit()
    return make_response('', 204)


def delete_post(args):
    """Drop a post from the database"""

    post = query_postid(args.id)
    post.delete()

    DB.session.commit()
    return make_response('', 204)


def query_postid(post_id):
    """
    Get a post based on the postid or raise a BadRequest when not found.

    :param post_id: int, primary key for the post.
    :return: Table row representing a post.
    """
    post = Random.query.filter_by(postid=post_id).first()
    if not post:
        raise NotFound('Post not found')
        return 'Post not found'
    return post
