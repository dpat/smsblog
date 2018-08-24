import time
import json
from datetime import datetime, timedelta
from twilio.rest import Client
from threading import Thread
from ..routes.reminder import get_reminder, delete_reminder


def initiate_reminders(app):
    query_reminders(app)


class query_reminders(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.app = app
        self.daemon = True
        self.start()
    def run(self):
        while True:
            send_reminders(self.app)
            time.sleep(1)


def send_reminder(message, app):
    account_sid = app.config.get('sid')
    auth_token = app.config.get('auth_token')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                  body=message,
                                  from_=app.config.get('tnum'),
                                  to=app.config.get('num')
                              )


def send_reminders(app):
    reminders = get_reminder('all')
    reminders = json.loads((reminders.data).decode('utf-8'))
    for reminder in reminders:
        date = reminder['date']
        days = reminder['days']
        time = reminder['time']
        if days == '.':
            days = 1
        if time == '.':
            time = str(date.hour) + str(date.minute)
        recurring = reminder['recurring']
        message = reminder['message']
        next_reminder = (date + timedelta(days=int(days))).replace(
                         hour=int(time[:2]), minute=int(time[2:]))
        next_reminder = '{:Y-:m-:d-:H-:M}'.format(next_reminder)
        now = '{:Y-:m-:d-:H-:M}'.format(datetime.utcnow())

        if now == next_reminder:
            send_reminder(message, app)
            if recurring == 'once':
                delete_reminder(reminder['reminderid'])

        if now > next_reminder:
            if recurring == 'daily':
                next_reminder = '{:H-:M}'.format(next_reminder)
                now = '{:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message, app)
            elif recurring == 'weekly':
                next_reminder = '{:a-:H-:M}'.format(next_reminder)
                now = '{:a-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message, app)
            elif recurring == 'monthly':
                next_reminder = '{:d-:H-:M}'.format(next_reminder)
                now = '{:d-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message, app)
            elif recurring == 'yearly':
                next_reminder = '{:m-:d-:H-:M}'.format(next_reminder)
                now = '{:m-:d-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message, app)
            elif recurring == 'once':
                send_reminder(message, app)
                delete_reminder(reminder['reminderid'])
