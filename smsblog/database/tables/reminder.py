"""The reminder table."""

import datetime
from .. import DB


class Reminder(DB.Model):
    """
    Reminder Table.

    reminderid: Integer, Unique identifier for a reminder.
    reminder: Text, The text of the reminder.
    date: DateTime, Date of the reminder's creation
    days: Integer, At what day interval to send reminder.
    time = Integer, At what time of day (UTC) to send reminder
    recurring = Text, At what interval to resend reminder
                hourly - daily - weekly - monthly - yearly
    """

    __tablename__ = 'reminder'
    reminderid = DB.Column(DB.Integer, nullable=False, primary_key=True)
    reminder = DB.Column(DB.Text, nullable=False)
    date = DB.Column(DB.DateTime, nullable=False,
                     default=datetime.datetime.utcnow)
    days = DB.Column(DB.Integer, nullable=False)
    time = DB.Column(DB.Integer, nullable=False)
    recurring = DB.Column(DB.Text, nullable=False)
