"""
Test core behaviour of changelog processing
"""

from datetime import date
from io import StringIO
from pathlib import Path
from textwrap import dedent

import pytest
from packaging.version import Version

from clproc import parser
from clproc.exc import ClprocException
from clproc.model import (
    ChangelogEntry,
    ChangelogType,
    FileMetadata,
    FileMetadataField,
    IssueId,
    ParsingIssueMessage,
    ReleaseEntry,
    ReleaseInformation,
    TParseIssueHandler,
)
from clproc.parser import core

DATA_DIR = Path(__file__).parent / "data"
TEST_DATA = (DATA_DIR / "changelog.in").read_text(encoding="utf8")


def test_parse() -> None:
    """
    Make sure that parsing properly extracts releases and logs
    """
    result = parser.parse(StringIO(TEST_DATA)).changelog
    assert len(result.releases) == 2
    assert result.releases[0].version == Version("2.8")
    assert result.releases[1].version == Version("2.7")
    assert len(result.releases[0].logs) == 8
    assert len(result.releases[1].logs) == 7


def test_release_rows_compatibility() -> None:
    """
    As of mid 2022 a change was introduced to split release information into a
    separate source. This unit-test ensures that we have backwards
    compatibility.
    """
    data = StringIO(
        dedent(
            """\
        version; type    ; message
        2.1.0  ; release ; 2018-01-01; Hello World
        2.1.0  ; added   ; hello world   ;    ; ;h;          ;
               ; support ; goodbye world ;    ; ; ;2010-01-01;
    """
        )
    )
    changelog = parser.parse(data).changelog
    assert changelog.releases[0].release_date == date(2018, 1, 1)
    assert changelog.releases[0].notes.strip() == "Hello World"


def test_full_version() -> None:
    """
    Ensure the raw version number includes pre-releases
    """
    # pylint: disable=line-too-long
    test_data = dedent(
        """\
        version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

        2.8.1.post1 ; changed  ; Jenkins job fixed.
        2.8.1 ; changed  ; Jenkins job fixed.
        2.8.1rc2 ; changed  ; Removed hardcoded value from `fab autotest`.
        2.8.1rc1 ; added    ; Optional "path" argument to `fab autotest`.
        """
    )
    # pylint: enable=line-too-long
    result = parser.parse(StringIO(test_data)).changelog
    versions = [str(row.version) for row in result.releases[0].logs]
    assert versions == ["2.8.1.post1", "2.8.1", "2.8.1rc2", "2.8.1rc1"]


def test_patch_post_release() -> None:
    """
    Ensure that we allow "post" releases in the changelog
    """
    data = StringIO(
        dedent(
            """\
    version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

    2.8.1.post1 ; changed  ; Post-Release Test
    """
        )
    )
    result = parser.parse(data).changelog
    log = result.releases[0].logs[0]
    assert log.version == Version("2.8.1.post1")


def test_empty_file() -> None:
    """
    Ensure that we can parse an empty file properly
    """
    result = parser.parse(StringIO("")).changelog
    assert result.releases == tuple()


def test_aggregate_releases_limit() -> None:
    """
    We want to be able to limit the number of parsed releases
    """
    data = StringIO(
        dedent(
            """\
            1.2.0 ; changed  ; Foobar
            1.3.0 ; changed  ; Foobar
            1.4.0 ; changed  ; Foobar
            """
        )
    )
    result = parser.parse(data, num_releases=2).changelog
    assert len(result.releases) == 2


def test_invalid_meta_version() -> None:
    """
    When we specify an incorrect version, we want to get an appropriate error
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 999999.0 -*-
            1.2.3 ; changed  ; Foobar
            """
        )
    )
    with pytest.raises(ClprocException, match="infile version"):
        parser.parse(data)


def test_multiple_url_templates():
    """
    We should be able to specify more than one issue-url template
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            2.7.5 ; added    ; legacy format    ; 123
            2.7.5 ; added    ; implicit default ; 123, tpl2: 234
            2.7.5 ; added    ; explicit default ; default:123, tpl2: 234
            """
        )
    )
    result = parser.parse(data).changelog.releases[0].logs
    assert set(result[0].issue_ids) == {IssueId(123, "default")}
    assert set(result[1].issue_ids) == {
        IssueId(123, "default"),
        IssueId(234, "tpl2"),
    }
    assert set(result[2].issue_ids) == {
        IssueId(123, "default"),
        IssueId(234, "tpl2"),
    }


@pytest.mark.parametrize(
    "version, expected_notes, expected_date",
    [
        (Version("1.0"), "modified-notes", date(2000, 2, 3)),
        (Version("1.2"), "unmodified-notes", date(2000, 1, 1)),
        (Version("2.3"), "unmodified-notes", date(2000, 1, 1)),
    ],
)
def test_with_release_information(version, expected_notes, expected_date):
    """
    If a "release entry" matches with additional data from the release-file, we
    expect the meta-data to be updated (the release-file takes precedence). If
    the version does not match the release, the meta-data should remain
    unmodified.
    """
    entries = [
        ReleaseEntry(
            version=version,
            release_date=date(2000, 1, 1),
            notes="unmodified-notes",
            logs=(
                ChangelogEntry(
                    version=Version("1.2.3"),
                    type_=ChangelogType.ADDED,
                    is_internal=False,
                    is_highlight=False,
                    subject="log-entry-1",
                    issue_ids=core.parse_issue_ids("123"),
                    detail="log-detail-1",
                ),
            ),
        )
    ]
    with_info = core.with_release_information(
        entries,
        {
            Version("1.0"): ReleaseInformation(
                date=date(2000, 2, 3),
                notes="modified-notes",
            )
        },
    )
    result = list(with_info)
    assert result[0].release_date == expected_date
    assert result[0].notes == expected_notes
