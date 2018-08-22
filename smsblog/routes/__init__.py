"""All modules that are used for routes, and global methods."""

import json

from ..errors.badrequest import BadRequest

__all__ = [
    'answer',
    'certificate',
    'exam',
    'question',
    'section',
    'user'
]


def get_payload(request):
    """Get a payload from a request, or raise a BadRequest."""
    payload_raw = request.data
    payload_raw.decode()
    if not payload_raw:
        raise BadRequest('A payload for a user is required')
    payload_decode = payload_raw.decode()
    payload = json.loads(payload_decode)
    return payload
