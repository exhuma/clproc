"""
This module contains the common parsing logic for v1 and v2 of the changelog
template.

It centralises important (externally advertised) application logic which both
versions have in common.
"""

import csv
import logging
import re
from dataclasses import replace
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    TextIO,
    Tuple,
)

from packaging.version import InvalidVersion, Version

from clproc.exc import ChangelogFormatError
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
from clproc.reporting import default_parse_issue_handler
from clproc.textprocessing import get_multiline

LOG = logging.getLogger(__name__)
P_FILE_OPTION = re.compile(r"-\*- (?P<key>[a-z-]+):\s*?(?P<value>.*?)\s*?-\*-")


def _make_url_template(value: str) -> Tuple[str, str]:
    """
    Convert a prefixed URL into a tuple of both the prefix and value
    """
    lhs, _, rhs = value.strip().partition(";")
    if rhs:
        return lhs.strip(), rhs.strip()
    return "default", lhs.strip()


def parse_issue_ids(raw_text: str) -> Iterable[IssueId]:
    """
    Process issue IDs providing both the "source identifier" and the real
    issue-id.

    >>> list(parse_issue_ids("123, 234"))
    [IssueId(id=123, source="default"), IssueId(id=234, source="default")]

    >>> list(parse_issue_ids("123, src2:123"))
    [IssueId(id=123, source="default"), IssueId(id=123, source="src2")]
    """
    if not raw_text.strip():
        return
    for id_ in raw_text.split(","):
        lhs, _, rhs = id_.partition(":")
        if rhs:
            yield IssueId(int(rhs.strip()), lhs.strip())
        else:
            # No ":" found and the ID will be in the left-hand-side of the
            # partition
            yield IssueId(int(lhs.strip()))


def cleanup(row: List[str], changelog_version: Version) -> ChangelogEntry:
    """
    Cleanup values from the changelog rows and convert them to proper
    Python types.
    """

    if len(row) < 3:
        raise ChangelogFormatError(
            f"not enough fields/columns. Expected at least 3 but got {len(row)}"
        )

    version_raw = row[0].strip()
    type_ = row[1]
    subject = row[2]
    issue_ids_raw = row[3] if len(row) >= 4 else ""
    internal = row[4] if len(row) >= 5 else ""
    highlight = row[5] if len(row) >= 6 else ""
    # NOTE: Since version 2.0 of the changelog, the date-column (idx=6) is
    # ignored
    if changelog_version >= Version("2.0"):
        detail = row[6] if len(row) >= 7 else ""
    else:
        detail = row[7] if len(row) >= 8 else ""

    try:
        version = Version(version_raw)
    except InvalidVersion as exc:
        raise ChangelogFormatError(f"Invalid version: {version_raw!r}") from exc

    try:
        parsed_type = ChangelogType[type_.strip().upper()]
    except KeyError as exc:
        raise ChangelogFormatError(
            f"Unknown changelog type: {type_.strip()!r}. "
            f"Expected one of {[item.value for item in ChangelogType]}"
        ) from exc
    is_highlight = bool(highlight.strip())
    is_internal = bool(internal.strip())
    subject = subject.strip()
    issue_ids = frozenset(parse_issue_ids(issue_ids_raw))
    detail = get_multiline(detail)

    return ChangelogEntry(
        version=version,
        type_=parsed_type,
        is_internal=is_internal,
        is_highlight=is_highlight,
        subject=subject,
        issue_ids=issue_ids,
        detail=detail,
    )


def make_release_version(exact_version: Version, cutoff: int) -> Version:
    """
    Convert a detailed version into a release version.

    This simply returns the first "n" elements from the version.

    >>> make_release_version(Version("1.2.3"), 2)
    Version("1.2")
    >>> make_release_version(Version("1.2.3"), 3)
    Version("1.2.3")

    :param exact_version: The detailed version
    :param cutoff: How many elements to keep
    """
    release_version = Version(
        ".".join([str(x) for x in exact_version.release[:cutoff]])
    )
    return release_version


def propagate_first_col(
    rows: Iterable[List[str]],
) -> Generator[List[str], None, None]:
    """
    Iterate over items in *reader* and "fill in" missing valus in the first
    column.

    >>> list(propagate_first_col([["foo", "bar"], ["", "baz"]])
    [["foo", "bar"], ["foo", "baz"]]
    """
    last_seen_value = ""
    for row in rows:
        if len(row) >= 1 and row[0].strip() == "":
            yield [last_seen_value] + row[1:]
        elif len(row) >= 1 and row[0].strip() != "":
            last_seen_value = row[0]
            yield row
        else:
            yield row


def changelogrows(
    changelog_file: TextIO,
    changelog_version: Version,
    parsing_issue_handler: TParseIssueHandler,
) -> Generator[ChangelogEntry, None, None]:
    """
    Read *changelog_file* and generate "changelog entries" as they are
    encoutered.

    This takes care of cleanup and skipping wherever necessary. Each iteration
    on this generator contains a valid changelog item.
    """
    reader = csv.reader(changelog_file, delimiter=";", quotechar='"')
    for lineno, row in enumerate(propagate_first_col(reader), 1):
        # skip empty lines
        if not row:
            continue

        # Allow a sharp as comment line
        # (= whenever the value in the first column starts with a '#')
        if row[0].strip().startswith("#"):
            continue

        # Allow for unreleased entries
        if row[0].strip() == "unreleased":
            continue

        try:
            entry = cleanup(row, changelog_version)
        except ChangelogFormatError as exc:
            parsing_issue_handler(
                ParsingIssueMessage(logging.WARNING, f"Line #{lineno}: {exc}")
            )
            continue

        yield entry


def aggregate_releases(
    changelog_file: TextIO,
    file_metadata: FileMetadata = FileMetadata(),
    num_releases: int = 0,
    parse_issue_handler: TParseIssueHandler = default_parse_issue_handler,
) -> Generator[ReleaseEntry, None, None]:
    """
    Collect all (or a number of) release "blocks" in a changelog file.

    When ``num_releases`` is non-zero, return up to this many releases from the
    file.

    A release is delimited by the version number and as defined by the
    "release_nodes" value in ``file_metadata``. ``release_nodes`` defines the
    number of "positions" of a version number which delineate a release.

    For example, the version "1.2.3.4" is part of release "1.2" when using
    ``release_nodes=2`` and part of release "1.2.3" when using
    ``release_nodes=3``.
    """
    logs: List[ChangelogEntry] = []
    last_seen_release: Optional[Version] = None
    release_version: Optional[Version] = None
    emitted_releases = 0
    for entry in changelogrows(
        changelog_file, file_metadata.version, parse_issue_handler
    ):
        release_version = make_release_version(
            entry.version, file_metadata.release_nodes
        )
        if last_seen_release and last_seen_release != release_version:
            yield ReleaseEntry(last_seen_release, None, "", tuple(logs))
            emitted_releases += 1
            if emitted_releases == num_releases:
                return
            logs.clear()
        logs.append(entry)
        last_seen_release = release_version

    if logs:
        yield ReleaseEntry(last_seen_release, None, "", tuple(logs))


def extract_metadata(
    infile: TextIO, parse_issue_handler: TParseIssueHandler
) -> FileMetadata:
    # pylint: disable=line-too-long
    """
    Search *infile* for a line containing metadata following emacs style file
    headers::

        -*- changelog-version: 1.0 -*-
        -*- field: value -*-

    .. seealso:: https://www.gnu.org/software/emacs/manual/html_node/emacs/Specifying-File-Variables.html#Specifying-File-Variables
    """
    # pylint: enable=line-too-long
    initial_position = infile.tell()
    kwargs: dict[str, Any] = {}
    # Mapping from keyname as used in the file-content to the argument name of
    # the FileMetadata object. With a callable that converts the value from
    # string to the proper type.
    keydef: Mapping[FileMetadataField, Tuple[str, Callable[[str], Any]]] = {
        FileMetadataField.CHANGELOG_VERSION: ("version", Version),
        FileMetadataField.RELEASE_NODES: ("release_nodes", int),
        FileMetadataField.ISSUE_URL_TEMPLATE: (
            "issue_url_template",
            _make_url_template,
        ),
        FileMetadataField.RELEASE_FILE: ("release_file", str.strip),
    }
    try:
        for line in infile:
            matches = dict(P_FILE_OPTION.findall(line))
            if not matches:
                continue
            for field, (meta_kwarg, converter) in keydef.items():
                if field.value in matches:
                    # pylint: disable=not-callable
                    if field == FileMetadataField.ISSUE_URL_TEMPLATE:
                        container = kwargs.setdefault("issue_url_templates", {})
                        source, template = converter(matches[field.value])  # type: ignore # noqa
                        container[source] = template
                    else:
                        kwargs[meta_kwarg] = converter(matches[field.value])
    finally:
        infile.seek(initial_position)
    if "version" not in kwargs:
        clv_field = FileMetadataField.CHANGELOG_VERSION.value
        parse_issue_handler(
            ParsingIssueMessage(
                logging.WARNING, f"'-*- {clv_field}: x.y -*-' is missing"
            )
        )
    return FileMetadata(**kwargs)


def with_release_information(
    releases: Iterable[ReleaseEntry],
    additional_data: Dict[Version, ReleaseInformation],
) -> Iterable[ReleaseEntry]:
    """
    Augment the relase-entries with additional information from the "release
    file".

    :param releases: A collection of releases
    :param additional_data: A mapping from a release-version to the data
        provided in the release-file
    :return: An iterable over modified release entries, each with the
        additional data added to it.
    """
    for release in releases:
        if release.version:
            release_info = additional_data.get(release.version, None)
            if release_info:
                release = replace(
                    release,
                    release_date=release_info.date,
                    notes=release_info.notes,
                )
        yield release
