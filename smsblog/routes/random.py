"""Routes for modifying the Random table."""

import logging
from flask import Flask, jsonify, request, make_response, Blueprint
from sqlalchemy import inspect

from ..helpers.bphandler import BPHandler
from ..database import DB
from ..database.utils import add_value, table2dict
from ..database.tables.random import Random
from ..errors.badrequest import BadRequest
from ..errors.notfound import NotFound


RANDOM_BP = Blueprint('random', __name__)
BPHandler.add_blueprint(RANDOM_BP)


def collector(command):
    if command[0][:3] == '-c=':
        category = command[0][3:]
        post = command[1:]
        return add_post(category, post)
    else:
        return add_post('collected', command)


def handler(command):
    # yes I have tried argparse
    if command[0][0] == '-':
        if command[0][:5] == '-get=':
            post_id = command[0][5:]
            return get_post(post_id)
        if command[0][:3] == '-c=':
            category = command[0][3:]
            post = command[1:]
            return add_post(category, post)
        if command[0][:8] == '-udpate=':
            if command[1][:3] == '-c=':
                category = command[1][3:]
            else:
                category = 'General'
            post_id = command[0][8:]
            post = command[1:]
            return update_post(post_id, category, post)
        if command[0][:8] == '-delete=':
            post_id = command[0][8:]
            return delete_post(post_id)
    else:
        post = command
        return add_post('General', post)


def add_post(category, post):
    """Add a single post to the database."""

    post = ' '.join(post)
    random = {}
    values = {'category': category, 'post': post}
    for field in values.keys():
        if field in inspect(Random).mapper.column_attrs:
            random[field] = values[field]

    new = Random(**random)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def get_post(id):
    """Get a single post based on the post id, optionally
       return all posts if id=all"""

    if id == 'all':
        list_of_posts = []
        posts = Random.query.all()
        for post in posts:
            list_of_posts.append(table2dict(post))
        return make_response(jsonify(list_of_posts), 200)
    else:
        post_id = int(id)
        post = query_postid(post_id)
        return make_response(jsonify(table2dict(post)), 200)


def update_post(id, category, post):
    """Update a post based on its post id."""
    post_id = int(id)
    new_post = ' '.join(post)
    old_post = query_postid(post_id)
    values = {'category': category, 'post': new_post}
    for field in values.keys():
        if category == 'no_change':
            continue
        if field in inspect(Random).mapper.column_attrs:
            setattr(old_post, field, values[field])

    DB.session.commit()
    return make_response('', 204)


def delete_post(id):
    """Drop a post from the database"""

    post_id = int(id)
    post = query_postid(post_id)
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
