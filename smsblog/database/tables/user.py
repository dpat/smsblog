"""The user table."""
from .. import DB


class User(DB.Model):
    """
    User table.

    userid: Integer, generated user identifier for each user, always unique.
    admin: Boolean, When true, the user can access the full personal site.
    """

    __tablename__ = 'user'
    userid = DB.Column(DB.Integer, primary_key=True, nullable=False)
    admin = DB.Column(DB.Boolean, default=False, nullable=False)
