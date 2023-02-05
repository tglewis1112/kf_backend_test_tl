"""
Tests for api.outages
"""
import datetime
import json
import unittest

import httpretty

import outages_processor.api.outages
from outages_processor.constants import API_BASE_URL
from outages_processor.api.site import SiteDeviceInfo


class TestGetOutagesFilteredDatetime(unittest.TestCase):
    """
    Test suite for the get_outages_after_datetime function
    """

    @httpretty.activate
    def test_filtering_by_date_before_default(self):
        """
        GIVEN
        We request filtering of outage events
        WHEN
        The default cutoff is for events before 2022-01-01T00:00:00.000Z
        THEN
        We should receive a list of only outages beginning after the cutoff
        """
        outages = [
            {
                # Pre-boundary - should get filtered out
                "begin": "2021-07-26T17:09:31.036Z",
            },
            {
                # Marginal re-boundary - should get filtered out
                "begin": "2021-12-31T23:59:59.000Z",
            },
            {
                # Boundary value - should be allowed
                "begin": "2022-01-01T00:00:00.000Z",
            },
            {
                # Marginal post boundary - should be allowed
                "begin": "2022-01-01T00:00:01.000Z"
            },
            {
                # Post boundary - should be allowed
                "begin": "2023-01-01T00:00:00.000Z"
            },
        ]
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            body=json.dumps(outages),
        )
        returned_outages = outages_processor.api.outages.get_outages_after_datetime()
        self.assertEqual(outages[2:], list(returned_outages))

    @httpretty.activate
    def test_filtering_by_date_before_custom(self):
        """
        GIVEN
        We request filtering of outage events
        WHEN
        The provided cutoff is 2023-06-12T11:12:14.000Z
        THEN
        We should receive a list of only outages beginning after the cutoff
        """
        outages = [
            {
                # Pre-boundary - should get filtered out
                "begin": "2021-07-26T17:09:31.036Z",
            },
            {
                # Marginal re-boundary - should get filtered out
                "begin": "2021-12-31T23:59:59.000Z",
            },
            {
                # Boundary value - should be allowed
                "begin": "2023-06-12T11:12:14.000Z",
            },
            {
                # Marginal post boundary - should be allowed
                "begin": "2023-06-12T11:12:14.001Z"
            },
            {
                # Post boundary - should be allowed
                "begin": "2024-04-01T00:00:00.000Z"
            },
        ]
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            body=json.dumps(outages),
        )
        returned_outages = outages_processor.api.outages.get_outages_after_datetime(datetime.datetime(
            year=2023,
            month=6,
            day=12,
            hour=11,
            minute=12,
            second=14,
            tzinfo=datetime.timezone.utc,
        ))
        self.assertEqual(outages[2:], list(returned_outages))


class TestAddDeviceInfoToOutages(unittest.TestCase):
    """
    Test suite for the add_device_info_to_outages function
    """
    def test_device_association_with_valid_outage_id(self):
        """
        GIVEN
        An association request is made
        WHEN
        An outage and a device share a common ID
        THEN
        They should be associated correctly and returned
        """
        result = outages_processor.api.outages.add_device_info_to_outages(
            [
                {
                    "id": "3af21ee3-08cb-46e5-baa9-2c056d770494",
                    "another_field": "another_value",
                }
            ],
            {
                "3af21ee3-08cb-46e5-baa9-2c056d770494": SiteDeviceInfo("3af21ee3-08cb-46e5-baa9-2c056d770494", "DName")
            })
        expected = [
            {
                "id": "3af21ee3-08cb-46e5-baa9-2c056d770494",
                "another_field": "another_value",
                "name": "DName",
            },
        ]
        self.assertEqual(expected, result)

    def test_no_device_association_with_invalid_outage_id(self):
        """
        GIVEN
        An association request is made
        WHEN
        An outage and a device DO NOT share a common ID
        THEN
        The outage should be filtered (ignored)
        """
        result = outages_processor.api.outages.add_device_info_to_outages(
            [
                {
                    "id": "3af21ee3-08cb-46e5-baa9-2c056d770494",
                    "another_field": "another_value",
                }
            ],
            {
                "a1187fbb-e004-4bc7-861c-d487fa57f5f5": SiteDeviceInfo("a1187fbb-e004-4bc7-861c-d487fa57f5f5", "DName")
            })
        self.assertEqual([], result)

    def test_device_association_with_mixture_valid_invalid_outage_ids(self):
        """
        GIVEN
        An association request is made
        WHEN
        An outage and a device share a common ID, but another does not
        THEN
        They the first should be associated correctly and returned, and the second ignored
        """
        result = outages_processor.api.outages.add_device_info_to_outages(
            [
                {
                    "id": "3af21ee3-08cb-46e5-baa9-2c056d770494",
                    "another_field": "another_value",
                },
                {
                    "id": "a1187fbb-e004-4bc7-861c-d487fa57f5f5",
                    "another_field": "another_value_1",
                },
            ],
            {
                "3af21ee3-08cb-46e5-baa9-2c056d770494": SiteDeviceInfo("3af21ee3-08cb-46e5-baa9-2c056d770494", "DName")
            })
        expected = [
            {
                "id": "3af21ee3-08cb-46e5-baa9-2c056d770494",
                "another_field": "another_value",
                "name": "DName",
            },
        ]
        self.assertEqual(expected, result)
