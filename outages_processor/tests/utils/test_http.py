"""
Tests for utils.api
"""
import json
import unittest.mock

import httpretty
import requests

import outages_processor.utils.http
from outages_processor.constants import API_BASE_URL, API_KEY, HTTP_TIMEOUT_SECONDS
from outages_processor.utils.errors import APIError


class TestCreateSession(unittest.TestCase):
    """
    Test suite for the create_session function
    """

    def test_returns_valid_session(self):
        """
        GIVEN
        The function is called correctly
        WHEN
        I pass no arguments (defaults)
        THEN
        I should receive an instance of a requests session object
        """
        session = outages_processor.utils.http.create_session()
        self.assertIsInstance(session, requests.Session)

    def test_returns_correct_retries_defaults(self):
        """
        GIVEN
        The function is called
        WHEN
        I pass no arguments (defaults)
        THEN
        I should receive a session with three retries embedded
        """
        session = outages_processor.utils.http.create_session()
        self.assertEqual(3, session.adapters.get("http://").max_retries.total)

    def test_returns_valid_session_four_retries(self):
        """
        GIVEN
        The function is called
        WHEN
        I pass a maximum retries of four
        THEN
        I should receive a session with four retries embedded
        """
        session = outages_processor.utils.http.create_session(retries=4)
        self.assertEqual(4, session.adapters.get("http://").max_retries.total)


class TestAPIRequest(unittest.TestCase):
    """
    Test suite for the api_request function.
    """

    def setUp(self):
        """
        Common setup, shared across the suite
        """
        self.outages_get_body = [
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2021-07-26T17:09:31.036Z",
                "end": "2021-08-29T00:37:42.253Z",
            },
        ]

        self.standard_headers = {
            "x-api-key": API_KEY,
        }

    def test_api_request_get_correct_requests_call(self):
        """
        GIVEN
        I call the function with a GET request to /outages
        WHEN
        The function makes a HTTP call on the requests session
        THEN
        The arguments should indicate a GET method to the base URL concatenated with /outages
        """
        mock_create_session = unittest.mock.MagicMock()
        with unittest.mock.patch("outages_processor.utils.http.create_session", return_value=mock_create_session):
            outages_processor.utils.http.api_request("GET", "/outages")

        mock_create_session.request.assert_called_once_with(
            method="GET",
            url=f"{API_BASE_URL}/outages",
            headers=self.standard_headers,
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    def test_api_request_get_correct_requests_call_with_no_leading_slash(self):
        """
        GIVEN
        I call the function with a GET request to outages (no leading /)
        WHEN
        The function makes a HTTP call on the requests session
        THEN
        The arguments should indicate a GET method to the base URL concatenated with /outages
        """
        mock_create_session = unittest.mock.MagicMock()
        with unittest.mock.patch("outages_processor.utils.http.create_session", return_value=mock_create_session):
            outages_processor.utils.http.api_request("GET", "outages")
        mock_create_session.request.assert_called_once_with(
            method="GET",
            url=f"{API_BASE_URL}/outages",
            headers=self.standard_headers,
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    def test_api_request_post_correct_requests_call_no_data(self):
        """
        GIVEN
        I call the function with a POST request with no data to /site-outages/norwich-pear-tree
        WHEN
        The function makes a HTTP call on the requests session
        THEN
        The arguments should indicate a POST method to the base URL concatenated with /site-outages/norwich-pear-tree
        """
        mock_create_session = unittest.mock.MagicMock()
        with unittest.mock.patch("outages_processor.utils.http.create_session", return_value=mock_create_session):
            outages_processor.utils.http.api_request("POST", "/site-outages/norwich-pear-tree")

        mock_create_session.request.assert_called_once_with(
            method="POST",
            url=f"{API_BASE_URL}/site-outages/norwich-pear-tree",
            headers=self.standard_headers,
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    def test_api_request_post_correct_requests_call_with_data(self):
        """
        GIVEN
        I call the function with a POST request with JSON data to /site-outages/norwich-pear-tree
        WHEN
        The function makes a HTTP call on the requests session
        THEN
        The arguments should indicate a POST method to the base URL concatenated with /site-outages/norwich-pear-tree
        and a JSON payload
        """
        json_data = {
            "some_key": "some_value",
        }
        mock_create_session = unittest.mock.MagicMock()
        with unittest.mock.patch("outages_processor.utils.http.create_session", return_value=mock_create_session):
            outages_processor.utils.http.api_request("POST",
                                                     "/site-outages/norwich-pear-tree",
                                                     json=json_data)

        mock_create_session.request.assert_called_once_with(
            method="POST",
            url=f"{API_BASE_URL}/site-outages/norwich-pear-tree",
            headers=self.standard_headers,
            json=json_data,
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    @httpretty.activate
    def test_api_request_get(self):
        """
        GIVEN
        I call the function with a GET request to /outages
        WHEN
        The server responds gracefully with the expected data
        THEN
        I should receive a response object back with the correct data
        :return:
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            body=json.dumps(self.outages_get_body),
        )
        response = outages_processor.utils.http.api_request("GET", "/outages")
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.outages_get_body, response.json())

    @httpretty.activate
    def test_api_request_post(self):
        """
        GIVEN
        I call the function with a POST request to /site-outages/norwich-pear-tree
        WHEN
        The server responds gracefully with a 200 response
        THEN
        I should receive a response object back with a 200 status code
        :return:
        """
        httpretty.register_uri(
            httpretty.POST,
            f"{API_BASE_URL}/site-outages/norwich-pear-tree",
            status=200,
        )
        response = outages_processor.utils.http.api_request("POST", "/site-outages/norwich-pear-tree")
        self.assertEqual(200, response.status_code)

    @httpretty.activate
    @unittest.mock.patch("time.sleep")
    def test_api_request_retry_on_500_then_success(self, _):
        """
        GIVEN
        I call the function with a GET request to /outages
        WHEN
        The server responds twice with a 500 error followed by a 200
        THEN
        I should receive a response object back with the correct data
        :return:
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            responses=[
                httpretty.Response(status=500, body=""),
                httpretty.Response(status=500, body=""),
                httpretty.Response(status=200, body=json.dumps(self.outages_get_body)),
            ],
        )
        response = outages_processor.utils.http.api_request("GET", "/outages")
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.outages_get_body, response.json())

    @httpretty.activate
    @unittest.mock.patch("time.sleep")
    def test_api_request_retry_on_500_attempts_exceeded(self, _):
        """
        GIVEN
        I call the function with a GET request to /outages
        WHEN
        The server responds three times with a 500 error
        THEN
        The retries are exceeded and an APIError should be raised
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            status=500,
            body="",
        )
        with self.assertRaises(APIError):
            outages_processor.utils.http.api_request("GET", "/outages")

    @httpretty.activate
    def test_api_request_with_non_retry_code_400(self):
        """
        GIVEN
        I call the function with a GET request to /outages
        WHEN
        The server responds once with a 400 error
        THEN
        No retries are attempted and an APIError should be raised
        :return:
        """
        httpretty.register_uri(
            httpretty.GET,
            f"{API_BASE_URL}/outages",
            status=400,
            body="",
        )
        with self.assertRaises(APIError):
            outages_processor.utils.http.api_request("GET", "/outages")
