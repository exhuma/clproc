"""
This module ensures that we have a usable CLI interface
"""

import logging
from typing import Any
from unittest.mock import patch

import pytest
from packaging.version import Version

from clproc import cli
from clproc.exc import ClprocException


@pytest.mark.parametrize(
    "fmt, expected",
    [
        ("json", "json"),
        ("md", "markdown"),
        ("markdown", "markdown"),
    ],
)
def test_argument_parsing_format(fmt: str, expected: str) -> None:
    """
    We want the output format to be definable by CLI arg
    """
    args = cli.parse_args(["tests/data/changelog.in", "render", "-f", fmt])
    assert args.format == expected
    args = cli.parse_args(
        ["tests/data/changelog.in", "render", "--format", fmt]
    )
    assert args.format == expected


def test_missing_subcommand() -> None:
    """
    We want an error if we don't have a subcommand
    """
    with pytest.raises(SystemExit):
        cli.parse_args(["tests/data/changelog.in"])


def test_argument_parsing_infile() -> None:
    """
    A positional argument should be taken as input file
    """
    args = cli.parse_args(["tests/data/changelog.in", "render"])
    assert hasattr(args.infile, "read")


def test_render_call_spec() -> None:
    """
    We want the core implementation to be called with the proper arguments
    """
    with patch("clproc.core.make_changelog") as make_changelog:
        cli.main(["tests/data/changelog.in", "render", "-f", "json"])
    _, kwargs = make_changelog.call_args
    assert kwargs["fmt"] == "json"
    assert hasattr(kwargs["infile"], "read")


def test_check_call_spec() -> None:
    """
    We want the core implementation to be called with the proper arguments
    """
    with patch("clproc.core.check_changelog") as check_changelog:
        cli.main(["tests/data/changelog.in", "check", "1.2.3"])
    args, kwargs = check_changelog.call_args
    assert args == (Version("1.2.3"),)
    assert hasattr(kwargs["infile"], "read")


@pytest.mark.parametrize(
    "flag, kwarg",
    [
        ("--exact", "exact"),
        ("--strict", "strict"),
        ("--release-only", "release_only"),
    ],
)
def test_check_call_flags(flag, kwarg) -> None:
    """
    Make sure that boolean flags are passed into the internal call
    """
    with patch("clproc.core.check_changelog") as check_changelog:
        cli.main(["tests/data/changelog.in", "check", flag, "1.2.3"])
    args, kwargs = check_changelog.call_args
    assert kwargs[kwarg]


def test_known_error(caplog: Any) -> None:
    """
    If we have an uncaught error that is known by the internals (i.e. an
    instance of ClprocException), we want to have enough info in logging to
    debug, without overwhelming the default output
    """
    caplog.set_level(logging.DEBUG)
    with patch("clproc.cli.core") as core:
        core.make_changelog.side_effect = ClprocException("Yargs")
        cli.main(["-v", "tests/data/changelog.in", "render", "-f", "json"])
    assert [logging.INFO, logging.DEBUG, logging.ERROR] == [
        log.levelno for log in caplog.records
    ]
    assert [False, True, False] == [
        (log.exc_info is not None) for log in caplog.records
    ]


def test_failed_version_check(capsys: Any) -> None:
    """
    When a changelog does not contain the correct version, we want to see a CLI
    output
    """
    with patch("clproc.cli.core") as core:
        core.check_changelog.return_value = False
        cli.main(["tests/data/changelog.in", "check", "1.2"])
    captured = capsys.readouterr()
    assert "1.2 not found" in captured.err
    assert "changelog.in" in captured.err


def test_autocheck():
    """
    Make sure that we have a simple way to call clproc for automated processes
    """
    with patch("clproc.core.check_changelog") as check_changelog, patch(
        "clproc.cli.discover_version"
    ) as discover_version:
        discover_version.return_value = "1.2.3"
        cli.main(["changelog.in", "autocheck"])
    discover_version.assert_called_with()
    args, kwargs = check_changelog.call_args
    assert args == (Version("1.2.3"),)
    assert hasattr(kwargs["infile"], "read")
