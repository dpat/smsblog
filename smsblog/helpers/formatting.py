import json
import shlex


def response_string(response):
    status_code = str(response.status_code)
    text = json.loads((response.data).decode('utf-8'))
    return status_code + ' ' + str(text)


def request_args(request):
    message_body = str(request.form['Body'])
    message_body = message_body.replace('"', r'\"')
    message_body = message_body.replace("'", r"\'")
    args = shlex.split(message_body)
    return args
