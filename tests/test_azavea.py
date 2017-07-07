import unittest
import tempfile
import configparser

from azavea import Climate


class ClimateTest(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(b'[Azavea]\napi_token: XXXXXX\n')
            temp.flush()
            self.client = Climate(configfile=temp.name)

    def test_get_config_file_missing(self):
        with self.assertRaises(FileNotFoundError):
            self.client._get_config_file('.missing')

    def test_read_config_missing_section_header(self):
        with self.assertRaises(configparser.MissingSectionHeaderError):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b'api_token: XXXXXX\n')
                temp.flush()
                self.client._read_config(temp.name)

    def test_read_config_incorrect_section_header(self):
        with self.assertRaises(configparser.NoSectionError):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b'[IncorrectHeader]\napi_token: XXXXXX\n')
                temp.flush()
                self.client._read_config(temp.name)

    def test_read_config_missing_api_token(self):
        with self.assertRaises(KeyError):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b'[Azavea]\nmissing_key: XXXXXX\n')
                temp.flush()
                self.client._get_api_token(temp.name)

    def test_get_api_token(self):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b'[Azavea]\napi_token: XXXXXX\n')
                temp.flush()
                token=self.client._get_api_token(temp.name)
                self.assertEqual(token, 'XXXXXX')


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()