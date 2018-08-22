"""The token table."""
from .. import DB


class Token(DB.Model):
    """
    Token Table.

    token_id: int, Primary key for a single token.
    token: text, String representing a token.
    """

    __tablename__ = 'token'
    token_id = DB.Column(DB.Integer, primary_key=True, nullable=False)
    token = DB.Column(DB.Text, nullable=False)
