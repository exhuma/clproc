from datetime import date
from io import StringIO
from textwrap import dedent
from typing import Any, Dict
from unittest.mock import mock_open, patch

import pytest

from clproc.exc import ReleaseFormatError
from clproc.model import FileMetadata
from clproc.parser import extract_metadata, v2
from clproc.reporting import default_parse_issue_handler


@pytest.mark.parametrize(
    "data, error_match",
    [
        ('---\nmeta:\n  version: "99.0"', "1\\.0"),
        ("---\nmeta:\n  version: 1.0", "float"),
        ("---\nfoo:\n  bar: 10", "meta.version"),
        ('---\nmeta:\n  version: "1.0"', "releases"),
    ],
)
def test_version_format_error(data: str, error_match: str):
    """
    Errors in release-file metadata should have a helpful message
    """
    release_data = StringIO(data)
    release_data.name = f"<StringIO from {__file__}>"
    with pytest.raises(ReleaseFormatError) as error:
        v2.extract_release_information(StringIO(), release_data)
    error.match(error_match)


def test_no_release_file() -> None:
    """
    Ensure we don't crash if the release-file is empty
    """
    result = v2.extract_release_information(StringIO(), release_file=None)
    assert result == {}


@pytest.mark.parametrize(
    "version_str, data, error_match",
    [
        # Invalid date value
        ("10.0", {"date": "12345"}, "date.*12345"),
        # Invalid version string
        ("foobar", {"date": date(1990, 1, 1)}, "PEP440"),
        (10.0, {"date": date(1990, 1, 1)}, "float"),
    ],
)
def test_release_parsing_errors(
    version_str: str, data: Dict[str, Any], error_match: str
):
    """
    Ensure the relase-info blocks raise helpful errors
    """
    with pytest.raises(ReleaseFormatError) as error:
        v2.parse_release_info(version_str, data, __file__)
    error.match(error_match)


def test_release_information():
    """
    If we have additional information for a specific release, include that
    information to the parsed output
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            version; type    ; message
            2.1.0  ; added   ; hello world   ;    ; ;h;
                ; support ; goodbye world ;    ; ; ;
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    release_data = StringIO(
        dedent(
            """\
            ---
            meta:
              version: "1.0"
            releases:
              2.1.0:
                date: 2018-01-01
                notes:
                  Hello World
            """
        )
    )
    release_data.name = f"<StringIO from {__file__}>"
    my_open = mock_open()
    my_open.return_value = release_data
    with patch("clproc.parser.v2.open", my_open):
        changelog = v2.parse(data, FileMetadata(release_file="release.yaml"))
    my_open.assert_called_with("release.yaml", encoding="utf8")
    assert changelog.releases[0].release_date == date(2018, 1, 1)
    assert changelog.releases[0].notes.strip() == "Hello World"


def test_release_notes_markdown():
    """
    The release notes should be valid markdown and therefore should be returned
    unmodified.
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            version; type    ; message
            2.1.0  ; added   ; hello world
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    release_data = StringIO(
        dedent(
            """\
            ---
            meta:
              version: "1.0"
            releases:
              2.1.0:
                date: 2018-01-01
                notes: |
                    Some
                        Text
                            With newlines
                    That shoud not be wrapped or modified in any way. Which means that long-lines should also be accepted!
            """
        )
    )
    release_data.name = f"<StringIO from {__file__}>"
    my_open = mock_open()
    my_open.return_value = release_data
    with patch("clproc.parser.v2.open", my_open), patch(
        "clproc.parser.v2.exists"
    ) as exists:
        exists.return_value = True
        changelog = v2.parse(data, FileMetadata(release_file="foo"))
    assert changelog.releases[0].notes.splitlines() == [
        "Some",
        "    Text",
        "        With newlines",
        (
            "That shoud not be wrapped or modified in any way. "
            "Which means that long-lines should also be accepted!"
        ),
    ]


def test_release_information_no_date():
    """
    Release information should allow empty
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            # -*- release-file: tests/data/release.yaml -*-
            version; type    ; message
            2.1.0  ; added   ; hello world   ;    ; ;h;          ;
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    release_data = StringIO(
        dedent(
            """\
            ---
            meta:
              version: "1.0"
            releases:
              "2.1.0":
                notes:
                  Hello World
            """
        )
    )
    release_data.name = f"<StringIO from {__file__}>"
    metadata = extract_metadata(data, default_parse_issue_handler)
    my_open = mock_open()
    my_open.return_value = release_data
    with patch("clproc.parser.v2.open", my_open), patch(
        "clproc.parser.v2.exists"
    ) as exists:
        exists.return_value = True
        changelog = v2.parse(data, metadata)
    assert changelog.releases[0].release_date is None
    assert changelog.releases[0].notes.strip() == "Hello World"


def test_log_details():
    """
    Since 2.0 removed the "date" column we must ensure that the "detail" field
    is not dropped.
    """
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            # version; type    ; message ; issue-ids ; int ; high ; detail
            2.1.0  ; added   ; hello world   ;    ; ;h;This is a detail
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    metadata = extract_metadata(data, default_parse_issue_handler)
    changelog = v2.parse(data, metadata)
    assert changelog.releases[0].logs[0].detail == "This is a detail"


def test_metadata_multiple_templates():
    data = StringIO(
        dedent(
            """\
            # -*- changelog-version: 2.0 -*-
            # -*- issue-url-template: https://the-default-url/{id} -*-
            # -*- issue-url-template: prefixed;https://the-other-url/{id} -*-
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    metadata = extract_metadata(data, default_parse_issue_handler)
    assert metadata.issue_url_templates == {
        "default": "https://the-default-url/{id}",
        "prefixed": "https://the-other-url/{id}",
    }
