"""
Custom exception classes for use in the application
"""


class OutagesProcessorError(BaseException):
    """
    Base exception for all outages processor errors to inherit from
    """


class APIError(OutagesProcessorError):
    """
    Error class to be used when an error is experienced connecting to the API
    """
