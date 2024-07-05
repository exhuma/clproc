"""
The changelog processor aggregates multiple log-entries into a release.

A releas is defined by <n> leadeing version positions. For example, the version
1.2.3 could have a release "1.2" when using 2 positions or "1.2.3" when using 3.

This is useful to control parsing when using non-semver versioning schemes
(f.ex. calendar versioning) where it cannot be stated that it is always the
first two positions that define a release.
"""


from io import StringIO
from textwrap import dedent
from typing import List

import pytest
from packaging.version import Version

from clproc import parse


@pytest.mark.parametrize(
    "num_nodes, expected_releases",
    [
        (1, ["1"]),
        (2, ["1.2", "1.3"]),
        (3, ["1.2.1", "1.2.2", "1.3.3", "1.3.4"]),
    ],
)
def test_aggregate_v1(num_nodes: int, expected_releases: List[str]) -> None:
    """
    Ensure that we properly aggregate relase entries in changelog version 1.0
    """
    changelog = parse(
        StringIO(
            dedent(
                f"""\
                # -*- release-nodes: {num_nodes} -*-
                1.2.1 ; added ; foo
                1.2.2 ; added ; foo
                1.3.3 ; added ; foo
                1.3.4 ; added ; foo
                """
            )
        )
    ).changelog
    release_versions = [release.version for release in changelog.releases]
    assert release_versions == [Version(v) for v in expected_releases]


@pytest.mark.parametrize(
    "num_nodes, expected_releases",
    [
        (1, ["1"]),
        (2, ["1.2", "1.3"]),
        (3, ["1.2.1", "1.2.2", "1.3.3", "1.3.4"]),
    ],
)
def test_aggregate_v2(num_nodes: int, expected_releases: List[str]) -> None:
    """
    Ensure that we properly aggregate relase entries in changelog version 2.0
    """
    changelog = parse(
        StringIO(
            dedent(
                f"""\
                # -*- changelog-version: 2.0 -*-
                # -*- release-nodes: {num_nodes} -*-
                1.2.1 ; added ; foo
                1.2.2 ; added ; foo
                1.3.3 ; added ; foo
                1.3.4 ; added ; foo
                """
            )
        )
    ).changelog
    release_versions = [release.version for release in changelog.releases]
    assert release_versions == [Version(v) for v in expected_releases]
