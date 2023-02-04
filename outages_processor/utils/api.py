import requests
from requests.adapters import HTTPAdapter, Retry

from outages_processor.constants import API_BASE_URL, API_KEY
from outages_processor.utils.errors import APIError


def create_session(retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    """
    Create a requests session with retries enabled with the given parameters.
    :param retries: Maximum number of times to attempt the HTTP request
    :type retries: int
    :param backoff_factor: The backoff factor to feed into requests/urllib, this affects the delay urllib
    will leave between request attempts. See https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html
    :type backoff_factor: float
    :return: A requests session object with the retries configured correctly
    :rtype: requests.Session
    """
    session = requests.Session()
    retries = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def api_request(verb: str, route: str, json: dict = None) -> requests.Response:
    """
    Helper function to make a request to the API with the given HTTP verb and route.
    HTTP requests will be automatically retried three times.
    :param verb: HTTP verb to attach to the request, e.g. GET, POST
    :type verb: str
    :param route: Route to send the request to, relative to the API root URL. e.g. /outages
    :type route: str
    :param json: Optional JSON body to send with the request (if permitted for the method)
    :type json: dict
    :return: HTTP response object if successful, None otherwise
    :rtype: requests.Response
    :raises APIError: In the event of an issue connecting to the API or an unexpected HTTP response
    """
    processed_route = route.lstrip("/")
    url = f"{API_BASE_URL}/{processed_route}"
    session = create_session(retries=3)

    headers = {
        "x-api-key": API_KEY,
    }

    request_args = {
        "method": verb,
        "url": url,
        "headers": headers,
    }
    if json:
        request_args.update({
            "json": json,
        })

    try:
        response = session.request(**request_args)
    except requests.RequestException as exc:
        raise APIError("Failed to communicate with the outages API") from exc
    return response
