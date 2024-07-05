"""
Main package file
"""
__version__ = "1.0.0"
__exact_version__ = __version__

from .model import Changelog, ParseResult
from .parser import parse

__all__ = [
    "Changelog",
    "ParseResult",
    "parse",
]
