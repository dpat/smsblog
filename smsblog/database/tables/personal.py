"""The personal table."""
import datetime
from .. import DB


class Personal(DB.Model):
    """
    Personal Table.

    postid: Integer, Unique identifier for a post.
    category: Text, Category of the post.
    post: Text, Body of the post.
    """

    __tablename__ = 'personal'
    date = DB.Column(DB.DateTime, nullable=False,
                     default=datetime.datetime.utcnow)
    postid = DB.Column(DB.Integer, nullable=False, primary_key=True)
    title = DB.Column(DB.Text, nullable=False)
    category = DB.Column(DB.Text, nullable=False)
    post = DB.Column(DB.Text, nullable=False)
