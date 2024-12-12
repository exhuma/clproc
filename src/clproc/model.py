"""
This module contains the data-model used across clproc
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Callable, Dict, FrozenSet, NamedTuple, Optional, Tuple

from packaging.version import Version


class ChangelogType(Enum):
    """
    Possible values for the "type" column, sorted by importance & see
    http://keepachangelog.com/en/1.0.0/
    """

    ADDED = "added"
    CHANGED = "changed"
    SECURITY = "security"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    SUPPORT = "support"
    FIXED = "fixed"
    DOC = "doc"


class FileMetadataField(Enum):
    """
    Possible keys for file metadata
    """

    CHANGELOG_VERSION = "changelog-version"
    RELEASE_NODES = "release-nodes"
    ISSUE_URL_TEMPLATE = "issue-url-template"
    RELEASE_FILE = "release-file"


class ParsingIssueMessage(NamedTuple):
    """
    A message intended to be seen by the end-user that can be displayed for
    parsing errors.
    """

    level: int
    "A log-level (f.ex.: logging.INFO)"
    message: str
    "The message to emit to the end-user"


TParseIssueHandler = Callable[[ParsingIssueMessage], None]
"A type-alias for a callable that handles parsing issues"


class RowType(Enum):
    EMPTY = "empty"
    COMMENT = "comment"
    LOG = "log"
    EXCLUDED = "excluded"
    UNPARSED = "unparsed"
    RELEASE = "release"


class CsvColumns(NamedTuple):
    version_raw: str
    type: str
    subject: str
    issue_ids_raw: str = ""
    internal: str = ""
    highlight: str = ""
    detail: str = ""


@dataclass(frozen=True)
class FileMetadata:
    """
    Additional meta-data which is required to process changelogs.

    This data is not part of the changelog entries themselves, but required for
    processing in ``clproc``.
    """

    version: Version = Version("1.0")
    """
    The version of the changelog. This defaults to 1.0 for backwards
    compatibility. Old changelogs did not have a version so we need to default
    to this.
    """

    release_nodes: int = 2
    """
    How many "positions" in a version number belong to a "release".
    """

    issue_url_templates: Dict[str, str] = field(default_factory=dict)
    """
    A URL-template that is passed to the renderer to generate valid URLs for
    issues listed in the changelog.
    """

    release_file: str = ""
    """
    An additional file which containts release-information (dates,
    release-notes)
    """


@dataclass(frozen=True)
class ChangelogEntry:
    """
    A single entry of the changelog.

    This represents one atomic item of the log. Multiple of these logs are
    aggregated in a :py:class:`~.ReleaseEntry`.
    """

    version: Version
    """
    The version for which this entry was written
    """

    type_: ChangelogType = ChangelogType.ADDED
    """
    Which kind of modification this entry represents.
    See http://keepachangelog.com/en/1.0.0/
    """

    subject: str = ""
    """
    A short one-line summary of the change
    """

    is_internal: bool = False
    """
    An "internal" log is not necessarily interesting for most end-users. Unless
    they "opt-in" to see them. Renderers may choose to hide such entries.
    """

    is_highlight: bool = False
    """
    A "highlight" is something that renderers can choose to visually distinguish
    from other entries.
    """

    issue_ids: FrozenSet["IssueId"] = frozenset([])
    """
    A collection of issue identifiers (if any) related to this log entry.
    Renderers may choose to generate links to issue-trackers from such entries.
    """

    detail: str = ""
    """
    An optional multiline block of text to further explain what the change is
    all about.
    """


@dataclass(frozen=True)
class ChangelogRow:
    type: RowType
    parsed_content: Optional[ChangelogEntry] = None
    raw_line: str = ""


@dataclass(frozen=True)
class ReleaseEntry:
    """
    A "release" is a collection of log-entries and aggregates log-entries of
    multiple "smaller" versions.

    For example, a project might choose to aggregate all "minor/patch" changes
    into a single "release" to keep the changelog tidy at the risk of losing a
    bit of readability for small changes.
    """

    version: Optional[Version] = None
    """
    The version number for this particular release
    """

    release_date: Optional[date] = None
    """
    An optional date for the release
    """

    notes: str = ""
    """
    An optional multiline text-block explaining the details of this release.
    """

    logs: Tuple[ChangelogEntry, ...] = tuple()
    """
    A sorted collection of log-entries contained in this release.
    """

    def __lt__(self, other: "ReleaseEntry") -> bool:
        if other.version is None:
            return False
        if self.version is None:
            return True
        return self.version < other.version


@dataclass(frozen=True)
class Changelog:
    """
    The top-level changelog object. It wraps all "releases" of the parsed data.
    """

    releases: Tuple[ReleaseEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ParseResult:
    """
    Wrapper around the parsed changelog and the detected meta-data of the
    changelog.
    """

    changelog: Changelog
    "The changelog content"
    file_metadata: FileMetadata
    "The metadata detected in the input file"


@dataclass(frozen=True)
class ReleaseInformation:
    """
    This contains information pertaining to a release as a whole (as opposed to
    fine-grained information of a single log-entry).

    The information contained herein should be valid markdown
    """

    date: Optional[date]
    "The date when this release was created"
    notes: str
    "Additional release notes"


@dataclass(frozen=True)
class IssueId:
    """
    An issue ID is combined of the ID itself and a source indicator where that
    ID can be found. The source indicator is referenced in the changelog
    metadata.
    """

    id: int
    "The effective Issue ID"
    source: str = "default"
    "The key which links this to the appropriate URL template"
