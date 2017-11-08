#!/usr/bin/env python
from sensu_plugin.handler import SensuHandler
import requests

class SaltstackHandler(SensuHandler):
    required_keys = [
        'username',
        'password'
    ]

    def validate_settings(self):
        salt_settings = self.settings.get('saltstack')
        if not salt_settings:
            self.bail('no salt settings dict defined')

        for key in self.required_keys:
            if not salt_settings.get(key):
                self.bail('required salt setting missing - ' + key)
        
        return salt_settings

    def handle(self):
        self.salt_settings = self.validate_settings()

        salt_sls = self.event['check'].get('salt_sls')
        salt_orch = self.event['check'].get('salt_orch')

        if salt_sls:
            self.salt_api_post(func_type='sls', path=salt_sls)

        if salt_orch:
            self.salt_api_post(func_type='orch', path=salt_orch)

    def salt_api_post(self, func_type='sls', path=None):
	if not path:
            self.bail("no sls/orch path specified")

        if func_type == 'sls':
            post_data = {
                'username': self.salt_settings['username'],
                'password': self.salt_settings['password'],
                'eauth': self.salt_settings.get('eauth', 'auto'),
                'client': 'local',
                'tgt': self.event['client'],
                'fun': 'state.apply',
                'arg': [ path ]
            }
        else:
            post_data = {
                'username': self.salt_settings['username'],
                'password': self.salt_settings['password'],
                'eauth': self.salt_settings.get('eauth', 'auto'),
                'client': 'runner',
                'fun': 'state.orch',
                'arg': [ path ]
            }

        session = requests.Session()
        resp = session.post(self.salt_settings['url'] + '/run', 
                            json=post_data)
        # pprint(resp.json())

SaltstackHandler()
