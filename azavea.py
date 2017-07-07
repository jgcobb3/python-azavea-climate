import configparser
from os import path


class Climate(object):

    def __init__(self, authorized=True):

        if authorized:
            self.authorization = 'Authorization: Token {}'.format(self._get_api_token())

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

    def _get_api_token(self, configfile=".config"):

        keys = self._read_config(configfile)
        if 'api_token' in keys:
            return keys['api_token']
        else:
            raise KeyError('api_token not found in {}'.format(configfile))
