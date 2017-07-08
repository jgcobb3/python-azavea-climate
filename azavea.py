import logging
import configparser
from os import path
from urllib.parse import urljoin, urlparse
import json

from geopy.distance import vincenty
import requests

log = logging.getLogger(__name__)


class Climate(object):

    def __init__(self, configfile=".config"):

        self.baseurl = 'https://app.climate.azavea.com/api/'
        self.header = {'Authorization': 'Token {}'.format(self._get_api_token(configfile)),
                       'Origin': 'https://www.serch.us'}

    @staticmethod
    def _get_config_file(configfile):

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

    def _get(self, url, params=None):

        if not bool(urlparse(url).netloc):
            url = urljoin(self.baseurl,url)
        try:
            response = requests.get(url,
                                    params=params,
                                    headers=self.header)
            response.raise_for_status()
            log.info(response.url)
            result = json.loads(response.content.decode())
            return result
        except requests.exceptions.RequestException as e:
            log.error(e)
            raise e


class City(Climate):

    def __init__(self, lat, lon):
        super().__init__()
        self.lat = lat
        self.lon = lon
        self._feature = self._nearest_city()
        self.id = self._feature['id']

    def _nearest_city(self):
        result = super()._get('city/nearest',
                              {'lat': self.lat,
                               'lon': self.lon})
        return result['features'][0]

    def get_offset(self):

        pt1 = (self.lon, self.lat)
        pt2 = tuple(self._feature['geometry']['coordinates'])
        return vincenty(pt1, pt2).kilometers

    def get_boundary(self):

        return super()._get('city/{}/boundary'.format(self.id))

