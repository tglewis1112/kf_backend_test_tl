"""
Exports for the utils module
"""
from .errors import OutagesProcessorError
from .http import api_request
from .logging import get_logger

__all__ = [
    "api_request",
    "get_logger",
    "OutagesProcessorError",
]
