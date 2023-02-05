"""
Command line entry point script for the outages processor
"""
import argparse
import sys
import traceback

import outages_processor.api
import outages_processor.constants
import outages_processor.utils


logger = outages_processor.utils.get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parses incoming command line arguments
    :return: A namespace containing the parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser("Outages Processor")
    parser.add_argument("--site-name",
                        dest="site_name",
                        default=outages_processor.constants.SITE_NAME,
                        help="Name of the site to process enhanced outages for")
    return parser.parse_args()


def process_outages_inner(site_name: str) -> None:
    """
    Performs the inner logic to process the outages and enhance them with the device information
    :param site_name: The name of the site to process outages for
    :type site_name: str
    :raises: Any exception thrown by the API
    """
    # Fetch all outages from the API
    all_outages = outages_processor.api.outages.get_outages_after_datetime()
    logger.info("Found %s outages after cutoff date", len(all_outages))
    # Get site device info in a dict with device ids as keys
    site_devices_map = outages_processor.api.get_site_info(site_name, devices_map=True)
    logger.info("Found %s devices", len(site_devices_map.keys()))
    # Merge the outages and devices
    outages_with_devices = outages_processor.api.add_device_info_to_outages(all_outages, site_devices_map)
    logger.info("Outages with valid device IDs: %s", len(outages_with_devices))
    # Upload the enhanced info
    outages_processor.api.upload_site_outages(site_name, outages_with_devices)
    logger.info("Successfully uploaded enhanced outages information")


def process_outages():
    """
    Command line entry point, wraps the logic in an exception handler for error handling
    :return: Exits with code 0 if successful, 1 otherwise
    """
    args = parse_args()
    failed = True
    try:
        # Treat command line args as kwargs
        process_outages_inner(**vars(args))
        # If we get to here then everything completed successfully
        failed = False
    except outages_processor.utils.OutagesProcessorError as exc:
        logger.error("Failed to process outages. Error: %s", exc)
        logger.debug(traceback.format_exc())

    sys.exit(int(failed))


if __name__ == "__main__":
    process_outages()
