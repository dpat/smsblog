#!/usr/bin/env python3

from smsblog import smsblog


smsblog.setup_logging(debug=False, verbose=True)
app = smsblog.config_app('smsblog')
smsblog.BPHandler.register_blueprints(app)
smsblog.config_dabase(app)
application = app

# sudo apt install libapache2-mod-wsgi-py3
"""
"<VirtualHost *>
    #ServerName example.com

    WSGIDaemonProcess smsblog user=smsblog group=smsblog threads=5
    WSGIScriptAlias / /var/www/smsblog/smsblog.wsgi

    <Directory /var/www/smsblog>
        WSGIProcessGroup smsblog
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
"""
