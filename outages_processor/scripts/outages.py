"""
Command line entry point script for the outages processor
"""
import argparse

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


def process_outages():
    """
    Placeholder function to be used later as a command line entry point for the application.
    """
    args = parse_args()
    all_outages = outages_processor.api.outages.get_outages_after_datetime()
    logger.info("Found %s outages after cutoff date", len(all_outages))
    site_devices_map = outages_processor.api.get_site_info(args.site_name, devices_map=True)
    logger.info("Found %s devices", len(site_devices_map.keys()))
    outages_with_devices = outages_processor.api.add_device_info_to_outages(all_outages, site_devices_map)
    logger.info("Outages with valid device IDs: %s", len(outages_with_devices))
    outages_processor.api.upload_site_outages(args.site_name, outages_with_devices)
    logger.info("Successfully uploaded enhanced outages information")


if __name__ == "__main__":
    process_outages()
