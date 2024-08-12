"""
This module contains tests for the version discovery process
"""
from io import BytesIO
from textwrap import dedent
from unittest.mock import Mock, mock_open, patch

import pytest

from clproc import discovery

FAKE_TOML = dedent(
    """\
    [build-system]
    requires = ["setuptools >= 64.0"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "clproc"
    version = "1.1.0"
    """
)

FAKE_CARGO_TOML = dedent(
    """\
    [package]
    version = "1.1.0"
    """
)


def test_discover_pyproject():
    """
    Ensure that we can extract the version from a pyproject.toml file
    """
    contents = BytesIO(FAKE_TOML.encode("utf8"))
    result = discovery.from_pyproject(contents)
    assert result == "1.1.0"


def test_discover_npm():
    """
    Ensure that we can extract the version from a package.json file
    """
    contents = BytesIO(b'{"version": "1.1.0"}')
    result = discovery.from_package_json(contents)
    assert result == "1.1.0"


def test_discover_cargo_toml():
    """
    Ensure that we can extract the version from a cargo.toml file
    """
    contents = BytesIO(FAKE_CARGO_TOML.encode("utf8"))
    result = discovery.from_cargo_toml(contents)
    assert result == "1.1.0"


@pytest.mark.parametrize(
    "filename, handler_name",
    [
        ("package.json", "from_package_json"),
        ("pyproject.toml", "from_pyproject"),
        ("cargo.toml", "from_cargo_toml"),
    ],
)
def test_discover_delegation(filename: str, handler_name: str):
    """
    Ensure that the proper filename delegates to the right method
    """
    mocked_open = Mock()
    with patch("clproc.discovery.pkg_filename") as pkg_filename, patch(
        f"clproc.discovery.{handler_name}"
    ) as handler, patch("builtins.open", mock_open(mocked_open)):
        pkg_filename.return_value = filename
        discovery.discover_version()
        handler.assert_called()
        mocked_open.assert_called_with(filename, mode="rb")
