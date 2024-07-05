"""
This package contains everything related to transforming a "changelog"
python-object to a document of various types.

The ``create`` method is provided as factory for the supported renderers.
"""
from .base import create

__all__ = ["create"]
