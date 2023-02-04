"""
Logging helpers
"""
import logging
import os


def get_logger(name):
    """
    Returns an instance of a logger with a standard configuration and the given name
    :param name: The name to assign to the logger
    :return: A reference to the constructed logger
    """
    log_level = logging.INFO
    logger = logging.getLogger(name)
    if os.getenv("OP_DEBUG", "false").lower() == "true":
        log_level = logging.DEBUG
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
