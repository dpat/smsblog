import time
from datetime import datetime, timedelta
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client
from threading import Thread
from .routes import reminder


def initiate_reminders():
    query_reminders()


class query_reminders(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            send_reminders()
            time.sleep(1)


def send_reminder(message):
    account_sid = app.config.get('sid')
    auth_token = app.config.get('auth_token')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                  body=message,
                                  from_=app.config.get('tnum'),
                                  to=app.config.get('num')
                              )


def send_reminders():
    reminders = get_reminders('all')
    reminders = json.loads((response.data).decode('utf-8'))
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
        next_reminder = (date + timedelta(days=int(days)))
                       .replace(hour=int(time[:2]),minute=int(time[2:]))
        next_reminder = '{:Y-:m-:d-:H-:M}'.format(next_reminder)
        now =  '{:Y-:m-:d-:H-:M}'.format(datetime.utcnow())

        if now == next_reminder:
            send_reminder(message)
            if recurring = 'once':
                delete_reminder(reminder['reminderid'])

        if now > next_reminder:
            if recurring == 'daily':
                next_reminder = '{:H-:M}'.format(next_reminder)
                now = '{:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message)
            elif recurring == 'weekly':
                next_reminder = '{:a-:H-:M}'.format(next_reminder)
                now = '{:a-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message)
            elif recurring == 'monthly':
                next_reminder = '{:d-:H-:M}'.format(next_reminder)
                now = '{:d-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message)
            elif recurring == 'yearly':
                next_reminder = '{:m-:d-:H-:M}'.format(next_reminder)
                now = '{:m-:d-:H-:M}'.format(datetime.utcnow())
                if now == next_reminder:
                    send_reminder(message)
            elif once:
                send_reminder(message)
                delete_reminder(reminder['reminderid'])
