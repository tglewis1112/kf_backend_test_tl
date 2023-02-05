"""
Helpers for the site-* APIs
"""
from collections import namedtuple

import outages_processor.utils


class SiteDeviceInfo(namedtuple("_SiteDeviceInfo", ("id", "name"))):
    """
    Container class for holding site device information entries
    """


def get_site_info(site_name: str, devices_map: bool = True) -> dict:
    """
    Gets information about the given site from the API
    :param site_name: Site name to retrieve information for
    :type site_name: str
    :param devices_map: Set to True to convert the resulting information to a dictionary with device IDs as keys and
    full device info as values
    :type devices_map: bool
    :return: The JSON body if devices_map is False, a dictionary as per above if devices_map is True
    :rtype: dict
    :raises APIError: In the event of an issue connecting to the API or an unexpected HTTP response
    """
    response = outages_processor.utils.api_request("GET", f"/site-info/{site_name}").json()
    if devices_map:
        response = {
            item.get("id"): SiteDeviceInfo(item.get("id"), item.get("name")) for item in response.get("devices")
        }
    return response


def upload_site_outages(site_name: str, outages_with_devices: list[dict]) -> bool:
    """
    Uploads enhanced site outage information to the API
    :param site_name: Site name to associate enhanced outage information with
    :param outages_with_devices: A list of dicts, each containing a blob of enhanced outage data
    :return: True if the request completed successfully, False otherwise
    :rtype: bool
    :raises APIError: In the event of an issue connecting to the API or an unexpected HTTP response
    """
    response = outages_processor.utils.api_request("POST", f"/site-outages/{site_name}", json=outages_with_devices)
    return response.ok
