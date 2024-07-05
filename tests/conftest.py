"""
Global configuration for pytest (see the pytest docs for details on conftest.py)
"""
from datetime import date

import pytest
from packaging.version import Version

from clproc.model import (
    Changelog,
    ChangelogEntry,
    ChangelogType,
    IssueId,
    ReleaseEntry,
)


@pytest.fixture()
def sample_log() -> Changelog:
    """
    Provide a sample changelog with one entry containing all values
    """
    return Changelog(
        (
            ReleaseEntry(
                version=Version("1.2"),
                release_date=date(2000, 1, 2),
                notes="the-release-notes",
                logs=(
                    ChangelogEntry(
                        version=Version("1.2.3"),
                        type_=ChangelogType.CHANGED,
                        is_internal=True,
                        is_highlight=True,
                        subject="the-subject",
                        issue_ids=frozenset(
                            [
                                IssueId(1, "default"),
                                IssueId(2, "default"),
                            ]
                        ),
                        detail="the-detail",
                    ),
                ),
            ),
        )
    )
