"""
Unit Tests for the core/business functionality of clproc
"""

import logging
from io import StringIO
from typing import Any

import pytest
from packaging.version import Version

from clproc import core


def test_make_cangelog() -> None:
    """
    Ensure that we can call "make_changelog" without error
    """
    data = StringIO("fake-header\n2.7.0 ; added ; foo ;;;;;")
    data.name = f"<stringio {__file__}>"
    output = core.make_changelog("json", data)
    assert isinstance(output, str)


@pytest.mark.parametrize(
    "wanted_version, content_version, expected_result",
    [
        ("1.2", "1.2.3.4", False),
        ("1.3", "1.2.3.4", False),
        ("1.2.3.4", "1.2.3.4", True),
        ("1.2", "", False),
        ("1.2", "1.2rc1", False),
        ("1.2", "1.2.post1", False),
        ("1.2", "1.2a1", False),
        ("1.2a1", "1.2a1", True),
    ],
)
def test_check_changelog_exact(
    wanted_version: str, content_version: str, expected_result: bool
) -> None:
    """
    We want to be able to check for an *exact* match
    """
    data = StringIO(f"# fake-header\n{content_version} ; added ; foo ;;;;;")
    result = core.check_changelog(Version(wanted_version), data, exact=True)
    assert result == expected_result


@pytest.mark.parametrize(
    "wanted_version, content_version, expected_result",
    [
        ("1.2.3.4rc1", "1.2.3.4", True),
        ("1.2.3.4rc1", "1.3.3.4", False),
        ("1.2.3.4rc1", "", False),
        ("1.2.3.4rc1", "1.2rc1", True),
        ("1.2.3.4rc1", "1.2.post1", True),
        ("1.2.3.4rc1", "1.2a1", True),
    ],
)
def test_check_changelog_release_only(
    wanted_version: str, content_version: str, expected_result: bool
) -> None:
    """
    Even when passing in an exact version (including non-release parts), we
    want to be able to check for only the release.
    """
    data = StringIO(f"# fake-header\n{content_version} ; added ; foo ;;;;;")
    result = core.check_changelog(
        Version(wanted_version), data, release_only=True
    )
    assert result == expected_result


@pytest.mark.parametrize(
    "wanted_version, content_version, expected_result",
    [
        ("1.2", "1.2.3.4", True),
        ("1.3", "1.2.3.4", False),
        ("1.2.3.4", "1.2.3.4", False),
        ("1.2", "", False),
        ("1.2", "1.2rc1", True),
        ("1.2", "1.2.post1", True),
        ("1.2", "1.2a1", True),
    ],
)
def test_check_changelog(
    wanted_version: str, content_version: str, expected_result: bool
) -> None:
    """
    Ensure that we can correctly check for missing entries
    """
    data = StringIO(f"# fake-header\n{content_version} ; added ; foo ;;;;;")
    result = core.check_changelog(Version(wanted_version), data)
    assert result == expected_result


@pytest.mark.parametrize(
    "broken_content, expected_message",
    [
        (
            "# -*- changelog-version: 2.0 -*-\nbroken-line\n1.2.3; added; baz",
            "Line #2: not enough fields/columns",
        ),
        (
            "# -*- changelog-version: 2.0 -*-\ninvalid-version; added; baz",
            "Line #2: Invalid version: 'invalid-version'",
        ),
        (
            "1.2.3; invalid-type; baz",
            "Line #1: Unknown changelog type: 'invalid-type'",
        ),
        ("# 1.2.3; added; baz", "'-*- changelog-version: x.y -*-' is missing"),
    ],
)
def test_strict_check(
    broken_content: str, expected_message: str, caplog: Any
) -> None:
    """
    Ensure that we can execute a "strict" check failing on everything causing an
    internal warning.
    """
    caplog.set_level(logging.WARNING)
    data = StringIO(broken_content)
    result = core.check_changelog(Version("1.2"), data, strict=True)
    for row in caplog.messages:
        print(row)
    assert any(
        expected_message in row for row in caplog.messages
    ), f"Expected message {expected_message!r} not found in logs"
    assert result is False


@pytest.mark.parametrize(
    "wanted_version, content_version, expected_result",
    [
        ("1991.01.02", "1991.01.02.03", True),
        ("1991.01.02", "1991.01.02", True),
    ],
)
def test_check_changelog_calver(
    wanted_version: str, content_version: str, expected_result: bool
) -> None:
    """
    Ensure that we can correctly check for missing entries when using
    calendar-versioning
    """
    data = StringIO(
        f"# -*- release-nodes: 3 -*-\n{content_version} ; added ; foo ;;;;;"
    )
    result = core.check_changelog(Version(wanted_version), data)
    assert result == expected_result


def test_make_unknown_renderer(caplog: Any) -> None:
    """
    If we create a non-existing renderer, we want a useful error message
    """
    infile = StringIO()
    infile.name = f"<stringio {__file__}>"
    result = core.make_changelog("this-is-an-unknown-renderer", infile)
    assert any("this-is-an-unknown-renderer" in msg for msg in caplog.messages)
    assert result == ""


def test_format() -> None:
    """
    Ensure that we can auto-format a ".in" file
    """
    data = StringIO(
        "\n".join(
            [
                "",
                "",
                "# -*- changelog-version: 2.0 -*-",
                "",
                "fake-header",
                "2.7.0 ;doc; foo ;;;;;",
                "2.7.0 ;added; hello world ;;;x;;",
                "",
                "# comment",
                "2.7.0 ;added; hello world 2 ;;;;i;",
                "",
                "",
            ]
        )
    )
    data.name = f"<stringio {__file__}>"
    output = core.format_changelog(data).getvalue()
    expected = "\n".join(
        [
            "2.7.0 ; doc   ; foo           ;;;   ;  ",
            "2.7.0 ; added ; hello world   ;;; h ;  ",
            "2.7.0 ; added ; hello world 2 ;;;   ; i",
            "",
        ]
    )
    assert output == expected
