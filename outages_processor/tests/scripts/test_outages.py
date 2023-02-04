"""
Tests for api.outages
"""
import argparse
import os
import unittest.mock

import httpretty

import outages_processor.scripts.outages
from outages_processor.constants import API_BASE_URL


class TestProcessOutages(unittest.TestCase):
    """
    Test suite for the process_outages function
    """
    def setUp(self):
        """
        Common setup, shared across the suite
        """
        with open(os.path.join(os.path.dirname(__file__), "outages_get.json"), "r", encoding="utf-8") as file_handle:
            self.outages_get_body = file_handle.read()

        with open(os.path.join(os.path.dirname(__file__), "site_info_get.json"), "r", encoding="utf-8") as file_handle:
            self.site_info_get_body = file_handle.read()

    @httpretty.activate
    def test_process_outages(self):
        """
        GIVEN
        I make a request to process the outages for a given site
        WHEN
        All required data can be retrieved successfully
        THEN
        A POST request with the correct payload should be sent
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
