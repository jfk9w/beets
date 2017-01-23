# -*- coding: utf-8 -*-

"""Updates a Kodi library whenever the beets library is changed. This is based on the Plex Update plugin.

Put something like the following in your config.yaml to configure:
    kodi:
        host: localhost
        port: 8080
        user: user
        pwd: secret
"""
from __future__ import division, absolute_import, print_function

import requests
from beets import config
from beets.plugins import BeetsPlugin


def update_kodi(host, port, user, password):
    """Sends request to the Kodi api to start a library refresh.
    """
    url = "http://{0}:{1}/jsonrpc/".format(host, port)

    # The kodi jsonrpc documentation states that Content-Type: application/json is mandatory
    headers = {'Content-Type': 'application/json'}
    # Create the payload. Id seems to be mandatory.
    payload = {'jsonrpc': '2.0', 'method':'AudioLibrary.Scan', 'id':1}
    r = requests.post(url, auth=(user, password), json=payload, headers=headers)
    return r

class KodiUpdate(BeetsPlugin):
    def __init__(self):
        super(KodiUpdate, self).__init__()

        # Adding defaults.
        config['kodi'].add({
            u'host': u'localhost',
            u'port': 8080,
            u'user': u'kodi',
            u'pwd': u'kodi'})

        self.register_listener('database_change', self.listen_for_db_change)

    def listen_for_db_change(self, lib, model):
        """Listens for beets db change and register the update for the end"""
        self.register_listener('cli_exit', self.update)

    def update(self, lib):
        """When the client exists try to send refresh request to Kodi server.
        """
        self._log.info(u'Updating Kodi library...')

        # Try to send update request.
        try:
            update_kodi(
                config['kodi']['host'].get(),
                config['kodi']['port'].get(),
                config['kodi']['user'].get(),
                config['kodi']['pwd'].get())
            self._log.info(u'... started.')

        except requests.exceptions.RequestException:
            self._log.warning(u'Update failed.')

