"""Routes for modifying the Blog table."""

import logging
from flask import Flask, jsonify, request, make_response, Blueprint
from sqlalchemy import inspect

from ..helpers.bphandler import BPHandler
from ..database import DB
from ..database.utils import add_value, table2dict
from ..database.tables.blog import Blog
from ..errors.badrequest import BadRequest
from ..errors.notfound import NotFound


BLOG_BP = Blueprint('blog', __name__)
BPHandler.add_blueprint(BLOG_BP)


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
                post = command[2:]
            else:
                category = 'no_change'
                post = command[1:]
            post_id = command[0][8:]
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
    blog = {}
    values = {'category': category, 'post': post}
    for field in values.keys():
        if field in inspect(Blog).mapper.column_attrs:
            blog[field] = values[field]

    new = Blog(**blog)
    add_value(new)

    return make_response(jsonify(table2dict(new)), 201)


def get_post(id):
    """Get a single post based on the post id, optionally
       return all posts if id=all"""

    if id == 'all':
        list_of_posts = []
        posts = Blog.query.all()
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

    new_post = query_postid(post_id)
    return make_response(jsonify(table2dict(new_post)), 204)


def delete_post(id):
    """Drop a post from the database"""

    post_id = int(id)
    post = query_postid(post_id)
    DB.session.delete(post)

    DB.session.commit()
    message = "blog post number (" + str(post_id) + ") deleted"
    return make_response(jsonify(message), 204)


def query_postid(post_id):
    """
    Get a post based on the postid or raise a BadRequest when not found.

    :param post_id: int, primary key for the post.
    :return: Table row representing a post.
    """
    post = Blog.query.filter_by(postid=post_id).first()
    if not post:
        raise NotFound('Post not found')
        return 'Post not found'
    return post
