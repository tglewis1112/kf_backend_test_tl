"""
Tests for api.site
"""
import json
import unittest

import httpretty

import outages_processor.api.site
from outages_processor.constants import API_BASE_URL


class TestGetSiteInfo(unittest.TestCase):
    """
    Test suite for the get_site_info function
    """
    def setUp(self):
        """
        Set up, shared across the test suite
        """
        self.site_data = {
            "id": "some-site-name",
            "name": "SomeSiteName",
            "devices": [
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "name": "Battery 1"
                },
                {
                    "id": "086b0d53-b311-4441-aaf3-935646f03d4d",
                    "name": "Battery 2"
                }
            ]
        }

    @httpretty.activate
    def test_get_site_info_raw(self):
        """
        GIVEN
        I call the function to retrieve site info
        WHEN
        I request raw data
        THEN
        The JSON data should be returned without manipulation
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/site-info/some-site-name",
            body=json.dumps(self.site_data),
        )
        result = outages_processor.api.site.get_site_info("some-site-name", devices_map=False)
        self.assertEqual(self.site_data, result)

    @httpretty.activate
    def test_get_site_info_map_convert(self):
        """
        GIVEN
        I call the function to retrieve site info
        WHEN
        I request the data parsed into a map
        THEN
        A dict should be returned with ids as keys and SiteDeviceInfo as values
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/site-info/some-site-name",
            body=json.dumps(self.site_data),
        )
        result = outages_processor.api.site.get_site_info("some-site-name", devices_map=True)
        self.assertEqual({
            "002b28fc-283c-47ec-9af2-ea287336dc1b":
                outages_processor.api.site.SiteDeviceInfo("002b28fc-283c-47ec-9af2-ea287336dc1b", "Battery 1"),
            "086b0d53-b311-4441-aaf3-935646f03d4d":
                outages_processor.api.site.SiteDeviceInfo("086b0d53-b311-4441-aaf3-935646f03d4d", "Battery 2")
        }, result)


class TestUploadSiteOutages(unittest.TestCase):
    """
    Test suite for the upload_site_outages function
    """
    @httpretty.activate
    def test_upload_site_outages(self):
        """
        GIVEN
        I call the API to upload site outages
        WHEN
        I provide valid data
        THEN
        A post request should be sent to the correct URL and True returned
        """
        httpretty.register_uri(
            httpretty.POST,
            f"{API_BASE_URL}/site-outages/some-other-site-name",
            body="",
        )
        device_data = [
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2021-07-26T17:09:31.036Z",
                "end": "2021-08-29T00:37:42.253Z",
                "name": "Device 1",
            },
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2022-05-23T12:21:27.377Z",
                "end": "2022-11-13T02:16:38.905Z",
                "name": "Device 2",
            },
        ]
        result = outages_processor.api.upload_site_outages("some-other-site-name", device_data)
        self.assertEqual(True, result)
