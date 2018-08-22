#!/usr/bin/env python3

from flup.server.fcgi import WSGIServer
from smsblog import smsblog


if __name__ == '__main__':
    smsblog.setup_logging(debug=False, verbose=True)
    app = smsblog.config_app('smsblog')
    smsblog.BPHandler.register_blueprints(app)
    smsblog.config_dabase(app)
    WSGIServer(app).run()
