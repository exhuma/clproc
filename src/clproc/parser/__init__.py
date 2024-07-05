"""
Entry point for changelog source parsing.

This file provides :py:func:`~.parse` which delegates to the appropriate parser
depending on detected changelog version.
"""
from typing import TextIO

from packaging.version import Version

from clproc.exc import ClprocException
from clproc.model import ParseResult, TParseIssueHandler
from clproc.parser.core import extract_metadata
from clproc.reporting import default_parse_issue_handler

from . import v1, v2


def parse(
    infile: TextIO,
    num_releases: int = 0,
    parse_issue_handler: TParseIssueHandler = default_parse_issue_handler,
) -> ParseResult:
    """
    Parse a changelog file and return the constructed
    :py:class:`clproc.model.Changelog` object

    This delegates to the appropriate parser for the given file.

    :param infile: The main changelog content
    :param parse_issue_handler: A callable which is called for every issue
        encountered during parsing. It gets a tuple with two elements: A
        severity (based on logging levels like ``logging.INFO``) and a message
    """
    file_metadata = extract_metadata(infile, parse_issue_handler)
    if file_metadata.version == Version("1.0"):
        return ParseResult(
            v1.parse(infile, file_metadata, num_releases, parse_issue_handler),
            file_metadata,
        )
    if file_metadata.version == Version("2.0"):
        return ParseResult(
            v2.parse(
                infile,
                file_metadata,
                num_releases,
                parse_issue_handler,
            ),
            file_metadata,
        )
    raise ClprocException(
        f"Unsupported infile version: {file_metadata.version}"
    )
