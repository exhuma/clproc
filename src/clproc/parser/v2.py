"""
Parser for the legacy (first version) changelog.in file
"""

import logging
from datetime import date
from os.path import exists
from typing import Any, Dict, List, Optional, TextIO, Tuple

from packaging.version import InvalidVersion, Version
from yaml import safe_load

from clproc.exc import ReleaseFormatError
from clproc.model import (
    Changelog,
    FileMetadata,
    ReleaseEntry,
    ReleaseInformation,
    TParseIssueHandler,
)
from clproc.parser.core import (
    aggregate_releases,
    with_release_information,
    changelogrows,
)
from clproc.reporting import default_parse_issue_handler

LOG = logging.getLogger(__name__)


def parse(
    changelog_file: TextIO,
    file_metadata: FileMetadata,
    num_releases: int = 0,
    parse_issue_handler: TParseIssueHandler = default_parse_issue_handler,
) -> Changelog:
    """
    Process changelog and release-note files into a
    :py:class:`clproc.model.Changelog` instance.

    :param changelog_file: A file-like object containing changelog entries.

    The changelog file is a valid CSV file as documented below. The release-file
    is a YAML file, documented in :py:func:`~.extract_release_information`.

    Returns a parsed list of log-entries given a CSV-file as input. The
    CSV-file must have the following columns::

        version;type;subject;issue_ids;internal;highlight;date;detail

    * The first line is skipped (assumed to be the header).
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

    Example::

        version;type;subject;issue_ids;internal;highlight;date;detail
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
    if file_metadata.release_file:
        if exists(file_metadata.release_file):
            with open(
                file_metadata.release_file, encoding="utf8"
            ) as release_file:
                release_information = extract_release_information(
                    changelog_file, release_file
                )
        else:
            LOG.error(
                "Release file %r not found. No release information "
                "will be available!",
                file_metadata.release_file,
            )
            release_information = {}
    else:
        release_information = {}

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
    changelog_file: TextIO, release_file: Optional[TextIO]
) -> Dict[Version, ReleaseInformation]:
    """
    Retrieve additional information for specific releases

    :param changelog_file: Ignored in this version
    :param release_file: a YAML file containing the release data
    """
    del changelog_file
    release_information: Dict[Version, ReleaseInformation] = {}
    if release_file is None:
        return release_information

    data = safe_load(release_file)
    try:
        release_notes_version = Version(data["meta"]["version"])
    except KeyError as exc:
        raise ReleaseFormatError(
            f"Release file {release_file.name} is missing the meta.version key"
        ) from exc
    except TypeError as exc:
        raise ReleaseFormatError(
            f"meta.version in the release file {release_file.name} "
            "must be a string but is "
            f"a {type(data['meta']['version']).__name__}!"
        ) from exc
    if release_notes_version != Version("1.0"):
        raise ReleaseFormatError(
            "We currently only support version 1.0 of the release file "
            f"{release_file.name}!"
        )
    if "releases" not in data:
        raise ReleaseFormatError(
            f"Missing key 'releases' in release file {release_file.name}"
        )
    for version_str, info in data["releases"].items():
        version, release_info = parse_release_info(
            version_str, info, release_file.name
        )
        release_information[version] = release_info
    return release_information


def parse_release_info(
    version_str: str, info: Dict[str, Any], filename: str
) -> Tuple[Version, ReleaseInformation]:
    """
    Try extracting necessary data from *info* raising helpful error messages
    where needed.

    :param version_str: The version of this release as seein in the input file.
    :param info: The key/value mapping of the release information.
    :param filename: The filename of the file which contains the additional data
    :returns: The parsed information.
    """
    release_date = info.get("date", None)
    if release_date is not None and not isinstance(release_date, date):
        raise ReleaseFormatError(
            "Release dates must be dates without time "
            f"(invalid value {release_date!r} in {filename})"
        )
    try:
        version = Version(version_str)
    except InvalidVersion as exc:
        raise ReleaseFormatError(
            f"Invalid version string in {filename}: "
            f"{version_str!r} is not PEP440 compliant!"
        ) from exc
    except TypeError as exc:
        raise ReleaseFormatError(
            f"Invalid version string in {filename}: "
            f"{version_str!r} (must be a string but is "
            f"a {type(version_str).__name__})"
        ) from exc
    return version, ReleaseInformation(release_date, info["notes"])
