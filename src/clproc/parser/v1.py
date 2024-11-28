"""
Parser for the legacy (first version) changelog.in file
"""
import csv
import logging
from dataclasses import replace
from datetime import date
from typing import Dict, List, TextIO

import dateutil.parser as dateutil
from packaging.version import InvalidVersion, Version

from clproc.model import (
    Changelog,
    FileMetadata,
    ParsingIssueMessage,
    ReleaseEntry,
    ReleaseInformation,
    TParseIssueHandler,
)
from clproc.parser.core import (
    aggregate_releases,
    changelogrows,
    make_release_version,
    propagate_first_col,
    with_release_information,
)
from clproc.reporting import default_parse_issue_handler

LOG = logging.getLogger(__name__)


def parse(
    changelog_file: TextIO,
    file_metadata: FileMetadata = FileMetadata(),
    num_releases: int = 0,
    parse_issue_handler: TParseIssueHandler = default_parse_issue_handler,
) -> Changelog:
    """
    Process changelog and release-note files into a
    :py:class:`clproc.model.Changelog` instance.

    :param changelog_file: A file-like object containing changelog entries.

    The changelog file is a "mostly" valid CSV file as documented below.

    Returns a parsed list of log-entries given a CSV-file as input. The
    CSV-file must have at least the first 3 of the following columns::

        version;type;subject;issue_ids;internal;highlight;date;detail

    * Any line starting with a ``#`` will be skipped
    * Any unparseable line will log an error and will be skipped.
    * Only the first three columns (version, type and subject) are mandatory.
    * Delimiter is a semicolon ``;``
    * Quote char is ``"``

    Some additional pre-processing is done to make authoring a CSV file
    easier:

    * All values ars stripped of whitespace. You can use it liberally to
      make the changelog readable.
    * If the "version" is left empty, the same as the previous line is
      taken (the first line must have a version)
    * The "detail" field may contain markdown format and may have
      newlines, but it must be quoted in that case.  Note that the
      quote-character *must* come right after the semi-colon (as per the CSV
      spec) for this to work! See the example below.  The field can also be
      indented for readability. This indentation will be automatically removed.
    * Versions should conform to :pep:`440`. This is a superset of SemVer 2.0.
    * The "highlight" and "internal" fields are boolean and any non-empty
      value is considered to be true (even "0")!
    * As of July/August 2022, the dates in normal log-entries are ignore. Dates
      must be added to the special "release" line. Please consider using
      changelog version 2.0 after July/August 2022.

    Release Lines:

    When the first column contains the word "release", the line is treated
    differently:

    The columns are: `version`, `"release" keyword`, `date`, `notes (optional)`

    This is used to add additional information to releases.

    Example::

        version;type;subject;issue_ids;internal;highlight;date;detail
        1.0   ; release ; 2018-01-01 ;"Some additional Release Notes
        Which can also be multiline and contain *markdown*"
        1.0   ; fixed   ; Finally fixed   ; 1234; * ; *  ; 2018-01-01 ;
              ; feature ; Added something ; 1234;   ;    ; 2018-01-01 ;"
                 ## Heading

                 Added something with more detail"
        0.5.2 ; fixed   ; Fix that        ;;;;2018-01-02 10:20:30 ;
        0.5.1 ; fixed   ; Fix this        ;;;;;

    The "type" column can have any of the values from :py:data:`~.ChangelogType`
    or the special value ``unreleased``. If the values is ``unreleased``, the
    line will be skipped. This allows developers to add entries into the
    changelog before the release is triggered.
    """

    file_position = changelog_file.tell()
    try:
        release_information = extract_release_information(
            changelog_file, parse_issue_handler
        )
    finally:
        changelog_file.seek(file_position)

    rows = changelogrows(
        changelog_file, file_metadata.version, parse_issue_handler
    )

    aggregated_releases = aggregate_releases(
        rows,
        file_metadata,
        num_releases,
        parse_issue_handler,
    )
    modified_releases: List[ReleaseEntry] = list(
        with_release_information(aggregated_releases, release_information)
    )
    return Changelog(tuple(modified_releases))


def extract_release_information(
    changelog_file: TextIO,
    parse_issue_handler: TParseIssueHandler = default_parse_issue_handler,
) -> Dict[Version, ReleaseInformation]:
    """
    Collect all special "release" lines

    Scans through the changelog file to find all lines containing the special
    "release" line and returns it as a mapping from the release-version to the
    given information.
    """
    reader = csv.reader(changelog_file, dialect='clproc')
    output: Dict[Version, ReleaseInformation] = {}
    for row in propagate_first_col(reader):
        # NOTE: Some of this parsing (like skipping comment-lines, e.t.c.) is
        # duplicated with the "clproc.core" module. This is caused by the
        # special "release" rows in the changelog v1.0 format. The complexity
        # should therefore *remaine here* and not pollute the rest of the code.
        # If we wanted to deduplicate code, we need to handle the special
        # "release" case in other areas where we don't really want it. So we
        # accept this duplication.
        if not row or row[0].strip().startswith("#"):
            continue
        version = row[0].strip()
        try:
            parsed_version = Version(version)
        except InvalidVersion as exc:
            parse_issue_handler(ParsingIssueMessage(logging.DEBUG, str(exc)))
            continue
        release_version = make_release_version(parsed_version, 2)
        if row and len(row) > 2 and row[1].strip().lower() == "release":
            date_string = row[2].strip()
            parsed_date = dateutil.parse(date_string).date()
            notes = ""
            if len(row) >= 4:
                notes = row[3].strip()
            output[release_version] = ReleaseInformation(
                parsed_date,
                notes,
            )
        elif row and len(row) > 7 and row[6].strip():
            date_string = row[6].strip()
            parsed_date = dateutil.parse(date_string).date()
            entry = output.get(
                release_version, ReleaseInformation(parsed_date, "")
            )
            entry = replace(
                entry, date=max(entry.date or date.min, parsed_date)
            )
            output[parsed_version] = entry
    return output
