"""The blog table."""
from .. import DB


class Blog(DB.Model):
    """
    Blog Table.

    postid: Integer, Unique identifier for a post.
    category: Text, Category of the post.
    post: Text, Body of the post.
    """

    __tablename__ = 'blog'
    postid = DB.Column(DB.Integer, nullable=False, primary_key=True)
    category = DB.Column(DB.Text, nullable=False)
    post = DB.Column(DB.Text, nullable=False)
