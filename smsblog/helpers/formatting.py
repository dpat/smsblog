import json
import shlex


def response_string(response):
    status_code = str(response.status_code)
    text = json.loads((response.data).decode('utf-8'))
    return str(text)


def request_sms_args(request):
    message_body = str(request.form['Body'])
    message_body = message_body.replace('"', r'\"')
    message_body = message_body.replace("'", r"\'")
    message_body = message_body.replace("\n", "<br/>")
    args = shlex.split(message_body)
#    for i in range(0, len(args)):
#        if args[i] == '---':
#            args[i] = '\n'
    return args


def request_api_args(request):
    payload_raw = request.data
    payload_decoded = payload_raw.decode()
    payload_decoded = payload_decoded.replace('"', r'\"')
    payload_decoded = payload_decoded.replace("'", r"\'")
    args = shlex.split(payload_decoded)
    return args
