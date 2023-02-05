"""
Outages interfaces for API communication
"""
import datetime

import outages_processor.utils


logger = outages_processor.utils.get_logger(__name__)


def get_outages_after_datetime(
        datetime_earliest: datetime.datetime = datetime.datetime.fromisoformat("2022-01-01T00:00:00.000Z")
) -> list:
    """
    Gets a list of outages filtered by time window.
    Any outages that began before the given datetime will be filtered out
    :param datetime_earliest: The datetime to use for filtering. Events occurring before this datetime
    will be filtered out.
    :return: A list of outages from the HTTP response body
    :rtype: list
    :raises APIError: In the event of an issue connecting to the API or an unexpected HTTP response
    """
    all_outages = outages_processor.utils.api_request("GET", "/outages").json()
    return [item for item in all_outages if datetime.datetime.fromisoformat(item.get("begin")) >= datetime_earliest]


def add_device_info_to_outages(outages: list[dict], site_devices_map: dict) -> list:
    """
    Enhances outage information with the name of the associated device.
    ! - Outages where the device does not exist in the map will be filtered out (ignored).
    :param outages: A list of outage events as dicts
    :type outages: list
    :param site_devices_map: A dictionary where the keys are device IDs and the values are device info dicts
    """
    outages_with_devices = []
    for outage in outages:
        outage_id = outage.get("id")
        device_info = site_devices_map.get(outage_id)
        if device_info:
            additional_info = {
                "name": device_info.name,
            }
            outage.update(additional_info)
            outages_with_devices.append(outage)
        else:
            logger.debug("No device info found for ID: %s", outage_id)

    return outages_with_devices
