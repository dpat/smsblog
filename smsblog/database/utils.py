"""Standard functions for working with database values."""
from sqlalchemy import inspect

from . import DB
from .tables import blog, personal, random, reminder, token, user


def create_tables():
    """Create all tables in the database."""
    DB.create_all()


def table2dict(table):
    """Take a query result for a table, and convert it to a dict."""
    return {attr.key: getattr(table, attr.key)
            for attr in inspect(table).mapper.column_attrs}


def add_value(entry):
    """Add a single database row to the database."""
    DB.session.add(entry)
    DB.session.commit()
    DB.session.refresh(entry)
