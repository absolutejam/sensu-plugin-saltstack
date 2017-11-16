#!/usr/bin/env python
from sensu_plugin.handler import SensuHandler
import re
import json
import requests


class SaltstackHandler(SensuHandler):
    '''
    Contact the SaltStack API server and run a state (.sls) on the client
    or run an orchestration.
    '''
    required_keys = [
        'username',
        'password'
    ]


    def handle(self):
        self.salt_settings = self.validate_settings()

        if self.event['check']['name'] == 'keepalive':
            # Get the /keepalive/ sls/orch path from the client config
            salt_sls = self.event['client'].get('salt', {}).get('keepalive_sls')
            salt_orch = self.event['client'].get('salt', {}).get('keepalive_orch')
        else:
            # Get the sls/orch path from the check config
            salt_sls = self.event['check'].get('salt_sls')
            salt_orch = self.event['check'].get('salt_orch')

        if salt_sls:
            self.salt_api_post(salt_sls, func_type='sls')

        if salt_orch:
            self.salt_api_post(salt_orch, func_type='orch')


    def validate_settings(self):
        '''
        Validate that all mandatory settings have been defined.
        '''
        salt_settings = self.settings.get('saltstack')

        if not salt_settings:
            self.bail('no salt settings dict defined')

        for key in self.required_keys:
            if not salt_settings.get(key):
                self.bail('required salt setting missing - ' + key)
        
        return salt_settings


    def get_client_name(self):
        '''
        Allow the client name to be inserted into a string, replacing
        the token '__client__'. This allows the sensu client to have
        a different name to the Salt minion, eg. if the Sensu client is
        only a hostname and the Salt minion is FQDN.

        First check to see if 'salt_clientmatch' has been defined in the check
        definition, otherwise fall back to 'salt_clientmatch' value in 
        settings, and finally just use the client name from the check output if
        neither have been defined.
        '''

        client_name = self.event['client'].get('name')
        client_sub = '(?i)__client__'

        check_clientmatch = self.event['check'].get('salt_clientmatch')
        client_config_clientmatch = self.event['client'].get('salt', {}).get('clientmatch')
        server_config_clientmatch = self.salt_settings.get('clientmatch')

        if check_clientmatch:
            return re.sub(client_sub, 
                          client_name,
                          check_clientmatch)
        elif client_config_clientmatch:
            return re.sub(client_sub,
                          client_name,
                          client_config_clientmatch)
        elif server_config_clientmatch:
            return re.sub(client_sub,
                          client_name,
                          server_config_clientmatch)
        else:
            return client_name
            
    def salt_api_post(self, path, func_type='sls'):
        if func_type == 'sls':
            post_data = {
                'username': self.salt_settings['username'],
                'password': self.salt_settings['password'],
                'eauth': self.salt_settings.get('eauth', 'auto'),
                'client': 'local',
                'tgt': self.get_client_name(),
                'fun': 'state.sls',
                'arg': [ path ],
                'kwarg': {
                     "pillar": {
                          "event": self.event
                      }
                 }
            }
        else:
            post_data = {
                'username': self.salt_settings['username'],
                'password': self.salt_settings['password'],
                'eauth': self.salt_settings.get('eauth', 'auto'),
                'client': 'runner',
                'fun': 'state.orch',
                'arg': [ path ],
                'kwarg': {
                     "pillar": {
                          "event": self.event
                      }
                 }
            }

        session = requests.Session()
        resp = session.post(self.salt_settings['url'] + '/run', 
                            json=post_data)

SaltstackHandler()
