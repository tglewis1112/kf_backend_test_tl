"""
Tests for api.outages
"""
import argparse
import os
import unittest.mock
import warnings

import httpretty
import pytest
import requests

import outages_processor.scripts.outages
from outages_processor.constants import API_BASE_URL


def exception_callback(*args):
    """
    Mock exception callback, invokes a ConnectionError
    :param args: Positional arguments
    """
    raise requests.ConnectionError("Mock connection error")


class TestProcessOutages(unittest.TestCase):
    """
    Test suite for the process_outages function
    """
    def setUp(self):
        """
        Common setup, shared across the suite
        """
        warnings.simplefilter("ignore", category=pytest.PytestUnhandledThreadExceptionWarning)
        with open(os.path.join(os.path.dirname(__file__), "outages_get.json"), "r", encoding="utf-8") as file_handle:
            self.outages_get_body = file_handle.read()

        with open(os.path.join(os.path.dirname(__file__), "site_info_get.json"), "r", encoding="utf-8") as file_handle:
            self.site_info_get_body = file_handle.read()

    @httpretty.activate
    @unittest.mock.patch("sys.exit")
    def test_process_outages(self, mock_sys_exit):
        """
        GIVEN
        I make a request to process the outages for a given site
        WHEN
        All required data can be retrieved successfully
        THEN
        A POST request with the correct payload should be sent
        The script exits gracefully with code 0
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            body=self.outages_get_body,
            status=200,
        )
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/site-info/norwich-pear-tree",
            body=self.site_info_get_body,
            status=200,
        )
        httpretty.register_uri(
            httpretty.POST,
            f"{API_BASE_URL}/site-outages/norwich-pear-tree",
            body="",
            status=200,
        )
        parsed_args = argparse.Namespace(site_name="norwich-pear-tree")
        with unittest.mock.patch("outages_processor.scripts.outages.parse_args", return_value=parsed_args):
            outages_processor.scripts.outages.process_outages()
            request = httpretty.last_request()
            self.assertEqual("POST", request.method)
            # pylint: disable=no-member
            self.assertEqual([
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2022-05-23T12:21:27.377Z",
                    "end": "2022-11-13T02:16:38.905Z",
                    "name": "Battery 1",
                },
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2022-12-04T09:59:33.628Z",
                    "end": "2022-12-12T22:35:13.815Z",
                    "name": "Battery 1",
                },
                {
                    "id": "086b0d53-b311-4441-aaf3-935646f03d4d",
                    "begin": "2022-07-12T16:31:47.254Z",
                    "end": "2022-10-13T04:05:10.044Z",
                    "name": "Battery 2",
                },
            ], request.parsed_body)
        mock_sys_exit.assert_called_with(0)

    @httpretty.activate
    @unittest.mock.patch("sys.exit")
    def test_process_outages_api_error(self, mock_sys_exit):
        """
        GIVEN
        I make a request to process the outages for a given site
        WHEN
        One of the API calls fails with a HTTP 400 error
        THEN
        The script exits with code 1
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            body=self.outages_get_body,
            status=200,
        )
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/site-info/norwich-pear-tree",
            body=self.site_info_get_body,
            status=200,
        )
        httpretty.register_uri(
            httpretty.POST,
            f"{API_BASE_URL}/site-outages/norwich-pear-tree",
            body="",
            status=400,
        )
        parsed_args = argparse.Namespace(site_name="norwich-pear-tree")
        with unittest.mock.patch("outages_processor.scripts.outages.parse_args", return_value=parsed_args):
            outages_processor.scripts.outages.process_outages()
        mock_sys_exit.assert_called_with(1)

    @httpretty.activate
    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("sys.exit")
    def test_process_outages_http_timeout(self, mock_sys_exit, _):
        """
        GIVEN
        I make a request to process the outages for a given site
        WHEN
        One of the HTTP requests experiences a connection error
        THEN
        The script exits with code 1
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            status=200,
            body=exception_callback,
        )
        parsed_args = argparse.Namespace(site_name="norwich-pear-tree")
        with unittest.mock.patch("outages_processor.scripts.outages.parse_args", return_value=parsed_args):
            outages_processor.scripts.outages.process_outages()
        mock_sys_exit.assert_called_with(1)
