"""
This module contains unit-tests for the data-model of clproc
"""
import pytest
from packaging.version import Version

from clproc.model import ReleaseEntry


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (ReleaseEntry(Version("1.0")), ReleaseEntry(Version("2.0")), True),
        (ReleaseEntry(None), ReleaseEntry(Version("2.0")), True),
        (ReleaseEntry(Version("1.0")), ReleaseEntry(None), False),
    ],
)
def test_release_sortability(
    left: ReleaseEntry, right: ReleaseEntry, expected: bool
) -> None:
    """
    Release entries should be sortable
    """
    assert (left < right) is expected
