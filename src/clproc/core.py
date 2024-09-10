"""
Evrything related to parsing and rendering of the "changelog.in" file.
"""
import logging
from typing import List, TextIO

from packaging.version import Version

from clproc import parser
from clproc.model import ParsingIssueMessage
from clproc.parser.core import make_release_version
from clproc.renderer import create

LOG = logging.getLogger(__name__)


def make_changelog(
    fmt: str,
    infile: TextIO,
    num_releases: int = 0,
) -> str:
    """
    Converts a ``changelog.in`` file into a plain-text document.

    :param fmt: The type of document that should be created
    :param infile: A file-like object that contains the contents of the
        ``changelog.in`` file.
    :param num_releases: The amount of releases that should be rendered
        (0=unlimited).
    :returns: The generated document
    """
    LOG.info("Generating %s changelog from %r", fmt, infile.name)

    data = parser.parse(infile, num_releases)
    renderer = create(fmt)
    if not renderer:
        LOG.error("No renderer found for %s", fmt)
        return ""

    return renderer.render(data.changelog, data.file_metadata)


def check_changelog(
    expected_version: Version,
    infile: TextIO,
    strict: bool = False,
    exact: bool = False,
    release_only: bool = False,
) -> bool:
    """
    Return "True" if the changelog contains an entry for the given release
    version, "False" otherwise
    """
    parse_issues: List[ParsingIssueMessage] = []
    data = parser.parse(infile, parse_issue_handler=parse_issues.append)
    changelog = data.changelog
    meta = data.file_metadata
    if release_only:
        expected_version = make_release_version(
            expected_version, meta.release_nodes
        )
    for row in parse_issues:
        LOG.log(row.level if not strict else logging.ERROR, row.message)
    if strict and parse_issues:
        return False
    if exact:
        candidates = set()
        for release in changelog.releases:
            candidates.update([log.version for log in release.logs])
    else:
        candidates = {
            release.version for release in changelog.releases if release.version
        }
    return expected_version in candidates
