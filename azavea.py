import configparser
from os import path
from urllib.parse import urljoin
import json

import requests

class Climate(object):

    def __init__(self, configfile=".config"):

        self.baseurl = 'https://app.climate.azavea.com/api/'
        self.header = {'Authorization': 'Token {}'.format(self._get_api_token(configfile)),
                       'Origin': 'https://www.serch.us'}

    def _get_config_file(self, configfile):

        configpath = path.join(path.dirname(__file__), configfile)
        if not path.exists(configpath):
            raise FileNotFoundError(configpath)
        else:
            return configpath

    def _read_config(self, configfile):

        config = configparser.ConfigParser()
        config.read(self._get_config_file(configfile))
        try:
            return dict(config.items('Azavea'))
        except configparser.NoSectionError as e:
            raise e

    def _get_api_token(self, configfile):

        keys = self._read_config(configfile)
        if 'api_token' in keys:
            return keys['api_token']
        else:
            raise KeyError('api_token not found in {}'.format(configfile))

    def get(self, url, params=None):
        response = requests.get(urljoin(self.baseurl,url),
                                params=params,
                                headers=self.header)
        return json.loads(response.content.decode())