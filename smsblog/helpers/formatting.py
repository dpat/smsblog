import json


def response_string(response):
    status_code = json.dumps((str((response.status_code)).decode('utf-8')))
    text = json.dumps((response.data).decode('utf-8'))
    return status_code + ' ' + text
