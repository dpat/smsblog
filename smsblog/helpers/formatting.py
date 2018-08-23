import json


def response_string(response):
    status_code = str(response.status_code)
    text = json.dumps((response.data).decode('utf-8'))
    return status_code + ' ' + text
