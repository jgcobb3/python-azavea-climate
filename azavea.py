import logging
import configparser
from os import path
from urllib.parse import urljoin, urlparse
import json

from geopy.distance import vincenty
import requests
import pandas as pd
import pprint


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

    def model(self, name=None):
        if name:
            return self._get('model/{}'.format(name))
        else:
            return self._get('model/')

    def scenario(self, name=None):
        if name:
            return self._get('scenario/{}'.format(name))
        else:
            return self._get('scenario/')

    def indicator(self, name=None):
        if name:
            return self._get('indicator/{}'.format(name))
        else:
            return self._get('indicator/')


class City(Climate):

    def __init__(self, lon=None, lat=None, name=None, admin=None):
        super().__init__()
        self.lon = lon
        self.lat = lat
        self.name = name
        self.admin = admin
        if lon and lat:
            self._feature = self._nearest(lon, lat)
        elif name and admin:
            self._feature = self._query(name, admin)
        if self._feature:
            self.id = self._feature['id']
        else:
            self.id = None

    def __repr__(self):
        return pprint.saferepr(self._feature['properties'])

    def _nearest(self, lon, lat):
        result = self._get('city/nearest',
                              {'lon': lon,
                               'lat': lat})
        if result['features']:
            return result['features'][0]
        else:
            return None

    def _query(self, name, admin):
        result = self._get('city', params={'name': name,
                                           'admin': admin})
        if result['features']:
            return result['features'][0]
        else:
            return None

    def offset(self):
        if self.lon and self.lat:
            pt1 = (self.lon, self.lat)
            pt2 = tuple(self._feature['geometry']['coordinates'])
            return vincenty(pt1, pt2).kilometers
        else:
            return None

    def boundary(self):
        return self._get('city/{}/boundary'.format(self.id))

    def data(self, scenario, indicator):
        d = self._get('climate-data/{}/{}/indicator/{}/'\
                      .format(self.id, scenario, indicator))
        return pd.DataFrame(d['data']).transpose()


