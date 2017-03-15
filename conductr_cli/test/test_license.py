from conductr_cli.test.cli_test_case import CliTestCase, strip_margin
from conductr_cli import license
from conductr_cli.license import EXPIRY_DATE_DISPLAY_FORMAT
from unittest import TestCase
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError
import arrow
import datetime
import json


class TestPostLicense(CliTestCase):
    auth = ('username', 'password')
    server_verification_file = 'test_server_verification_file'

    args = {
        'dcos_mode': False,
        'scheme': 'https',
        'host': '10.0.0.1',
        'port': '9005',
        'base_path': '/',
        'api_version': '2',
        'conductr_auth': auth,
        'server_verification_file': server_verification_file
    }

    def test_success(self):
        license_file = MagicMock()

        mock_license_file_content = MagicMock()
        mock_open = MagicMock(return_value=mock_license_file_content)

        mock_post = self.respond_with(status_code=200)

        input_args = MagicMock(**self.args)

        with patch('builtins.open', mock_open), \
                patch('conductr_cli.conduct_request.post', mock_post):
            self.assertTrue(license.post_license(input_args, license_file))

        mock_open.assert_called_once_with(license_file, 'rb')
        mock_post.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license',
                                          auth=self.auth,
                                          data=mock_license_file_content,
                                          verify=self.server_verification_file)

    def test_http_error(self):
        license_file = MagicMock()

        mock_license_file_content = MagicMock()
        mock_open = MagicMock(return_value=mock_license_file_content)

        mock_post = self.respond_with(status_code=500)

        input_args = MagicMock(**self.args)

        with patch('builtins.open', mock_open), \
                patch('conductr_cli.conduct_request.post', mock_post):
            self.assertRaises(HTTPError, license.post_license, input_args, license_file)

        mock_open.assert_called_once_with(license_file, 'rb')
        mock_post.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license',
                                          auth=self.auth,
                                          data=mock_license_file_content,
                                          verify=self.server_verification_file)

    def test_endpoint_not_supported(self):
        license_file = MagicMock()

        mock_license_file_content = MagicMock()
        mock_open = MagicMock(return_value=mock_license_file_content)

        mock_post = self.respond_with(status_code=503)

        input_args = MagicMock(**self.args)

        with patch('builtins.open', mock_open), \
                patch('conductr_cli.conduct_request.post', mock_post):
            self.assertFalse(license.post_license(input_args, license_file))

        mock_open.assert_called_once_with(license_file, 'rb')
        mock_post.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license',
                                          auth=self.auth,
                                          data=mock_license_file_content,
                                          verify=self.server_verification_file)


class TestGetLicense(CliTestCase):
    auth = ('username', 'password')
    server_verification_file = 'test_server_verification_file'

    args = {
        'dcos_mode': False,
        'scheme': 'https',
        'host': '10.0.0.1',
        'port': '9005',
        'base_path': '/',
        'api_version': '2',
        'conductr_auth': auth,
        'server_verification_file': server_verification_file
    }

    license = {
        'user': 'cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend',
        'maxConductrAgents': 3,
        'conductrVersions': ['2.1.*'],
        'expires': '2018-03-01T00:00:00Z',
        'grants': ['akka-sbr', 'cinnamon', 'conductr'],
    }

    license_json_text = json.dumps(license)

    def test_license_found(self):
        mock_get = self.respond_with(status_code=200, text=self.license_json_text)

        input_args = MagicMock(**self.args)

        with patch('conductr_cli.conduct_request.get', mock_get):
            is_license_success, license_result = license.get_license(input_args)
            self.assertTrue(is_license_success)
            self.assertEqual(self.license, license_result)

        mock_get.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license', auth=self.auth)

    def test_license_not_found(self):
        mock_get = self.respond_with(status_code=404)

        input_args = MagicMock(**self.args)

        with patch('conductr_cli.conduct_request.get', mock_get):
            is_license_success, license_result = license.get_license(input_args)
            self.assertFalse(is_license_success)
            self.assertIsNone(license_result)

        mock_get.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license', auth=self.auth)

    def test_http_error(self):
        mock_get = self.respond_with(status_code=500)

        input_args = MagicMock(**self.args)

        with patch('conductr_cli.conduct_request.get', mock_get):
            self.assertRaises(HTTPError, license.get_license, input_args)

        mock_get.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license', auth=self.auth)

    def test_endpoint_not_supported(self):
        mock_get = self.respond_with(status_code=503)

        input_args = MagicMock(**self.args)

        with patch('conductr_cli.conduct_request.get', mock_get):
            is_license_success, license_result = license.get_license(input_args)
            self.assertFalse(is_license_success)
            self.assertIsNone(license_result)

        mock_get.assert_called_once_with(False, '10.0.0.1', 'https://10.0.0.1:9005/v2/license', auth=self.auth)


class TestFormatLicense(TestCase):
    license = {
        'user': 'cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend',
        'maxConductrAgents': 3,
        'conductrVersions': ['2.1.*', '2.2.*'],
        'expires': '2018-03-01T00:00:00Z',
        'grants': ['akka-sbr', 'cinnamon', 'conductr'],
    }

    formatted_expiry = 'formatted_expiry'

    def test_all_fields_present(self):
        mock_format_expiry = MagicMock(return_value=self.formatted_expiry)

        with patch('conductr_cli.license.format_expiry', mock_format_expiry):
            result = license.format_license(self.license)

            expected_result = strip_margin("""|Licensed To: cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend
                                              |Max ConductR agents: 3
                                              |Expires In: {}
                                              |ConductR Version(s): 2.1.*, 2.2.*
                                              |Grants: akka-sbr, cinnamon, conductr""".format(self.formatted_expiry))
            self.assertEqual(expected_result, result)

        mock_format_expiry.assert_called_once_with(self.license['expires'])

    def test_not_present_expiry(self):
        mock_format_expiry = MagicMock(return_value=self.formatted_expiry)

        license_no_expiry = self.license.copy()
        del license_no_expiry['expires']

        with patch('conductr_cli.license.format_expiry', mock_format_expiry):
            result = license.format_license(license_no_expiry)

            expected_result = strip_margin("""|Licensed To: cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend
                                              |Max ConductR agents: 3
                                              |ConductR Version(s): 2.1.*, 2.2.*
                                              |Grants: akka-sbr, cinnamon, conductr""")
            self.assertEqual(expected_result, result)

        mock_format_expiry.assert_not_called()

    def test_not_present_versions(self):
        mock_format_expiry = MagicMock(return_value=self.formatted_expiry)

        license_no_versions = self.license.copy()
        del license_no_versions['conductrVersions']

        with patch('conductr_cli.license.format_expiry', mock_format_expiry):
            result = license.format_license(license_no_versions)

            expected_result = strip_margin("""|Licensed To: cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend
                                              |Max ConductR agents: 3
                                              |Expires In: {}
                                              |Grants: akka-sbr, cinnamon, conductr""".format(self.formatted_expiry))
            self.assertEqual(expected_result, result)

        mock_format_expiry.assert_called_once_with(self.license['expires'])

    def test_not_present_grants(self):
        mock_format_expiry = MagicMock(return_value=self.formatted_expiry)

        license_no_grants = self.license.copy()
        del license_no_grants['grants']

        with patch('conductr_cli.license.format_expiry', mock_format_expiry):
            result = license.format_license(license_no_grants)

            expected_result = strip_margin("""|Licensed To: cc64df31-ec6b-4e08-bb6b-3216721a56b@lightbend
                                              |Max ConductR agents: 3
                                              |Expires In: {}
                                              |ConductR Version(s): 2.1.*, 2.2.*""".format(self.formatted_expiry))
            self.assertEqual(expected_result, result)

        mock_format_expiry.assert_called_once_with(self.license['expires'])


class TestFormatExpiry(TestCase):
    date_now = datetime.datetime(2018, 12, 1, 0, 0, 0, 0)
    next_year = datetime.datetime(2019, 12, 1, 0, 0, 0, 0)
    last_year = datetime.datetime(2017, 12, 1, 0, 0, 0, 0)

    def test_valid(self):
        mock_current_date = MagicMock(return_value=self.date_now)

        with patch('conductr_cli.license.current_date', mock_current_date):
            # License expires in 1 year
            expiry_date = self.next_year
            result = license.format_expiry(expiry_date=expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ'))

            expected_expiry_date_display = arrow.get(expiry_date).to('local').strftime(EXPIRY_DATE_DISPLAY_FORMAT)
            expected_result = '365 days ({})'.format(expected_expiry_date_display)
            self.assertEqual(expected_result, result)

    def test_expiring_today(self):
        mock_current_date = MagicMock(return_value=self.date_now)

        with patch('conductr_cli.license.current_date', mock_current_date):
            # License expires today
            expiry_date = self.date_now
            result = license.format_expiry(expiry_date=expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ'))

            expected_expiry_date_display = arrow.get(expiry_date).to('local').strftime(EXPIRY_DATE_DISPLAY_FORMAT)
            expected_result = 'Today ({})'.format(expected_expiry_date_display)
            self.assertEqual(expected_result, result)

    def test_expired(self):
        mock_current_date = MagicMock(return_value=self.date_now)

        with patch('conductr_cli.license.current_date', mock_current_date):
            # License expired last year
            expiry_date = self.last_year
            result = license.format_expiry(expiry_date=expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ'))

            expected_expiry_date_display = arrow.get(expiry_date).to('local').strftime(EXPIRY_DATE_DISPLAY_FORMAT)
            expected_result = 'Expired ({})'.format(expected_expiry_date_display)
            self.assertEqual(expected_result, result)