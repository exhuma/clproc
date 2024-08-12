"""
This module contains code to auto-discover the current version of the project.
"""
import json
from os.path import exists
from typing import IO, Callable, Dict

import tomli

from clproc.exc import ClprocException


def discover_version() -> str:
    """
    Discover the project version for the current working directory.
    """
    filename = pkg_filename()
    handlers: Dict[str, Callable[[IO[bytes]], str]] = {
        "pyproject.toml": from_pyproject,
        "package.json": from_package_json,
        "cargo.toml": from_cargo_toml,
    }
    with open(filename, mode="rb") as fptr:
        return handlers[filename](fptr)


def from_cargo_toml(data: IO[bytes]) -> str:
    """
    Discover the version from a cargo.toml file.

    :param data: A file handle to the metadata file.
    """
    metadata = tomli.load(data)  # type: ignore
    return metadata["package"]["version"]  # type: ignore


def from_pyproject(data: IO[bytes]) -> str:
    """
    Discover the version from a pyproject.toml file.

    :param data: A file handle to the metadata file.
    """
    metadata = tomli.load(data)  # type: ignore
    backend = metadata["build-system"]["build-backend"]
    if backend != "setuptools.build_meta":
        raise ClprocException(f"Unsupported Python build-backend: {backend!r}")
    return metadata["project"]["version"]  # type: ignore


def from_package_json(data: IO[bytes]) -> str:
    """
    Discover the version from a package.json file.

    :param data: A file handle to the metadata file.
    """
    metadata = json.load(data)
    return metadata["version"]  # type: ignore


def pkg_filename() -> str:  # pragma: no cover
    """
    Return the most appropriate package metadata filename for this project
    """
    precedence = ["pyproject.toml", "package.json"]
    for item in precedence:
        if exists(item):
            return item
    raise ClprocException("No valid project metadata file found!")
