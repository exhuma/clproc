"""
This module contains the definition of a renderer which transforms a changelog
object into a JSON document.
"""
import json
from datetime import date
from typing import Any, ClassVar, Dict, Iterable, List

from packaging.version import Version

from clproc.model import (
    Changelog,
    ChangelogEntry,
    ChangelogType,
    FileMetadata,
    IssueId,
)


class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for the JSONRenderer
    """

    # pylint: disable=method-hidden

    def default(self, o: Any) -> Any:
        if isinstance(o, frozenset):
            return list(o)
        if isinstance(o, Version):
            return str(o)
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, ChangelogType):
            return o.value
        return super().default(o)


def _issue_id_sort_key(item: IssueId) -> Any:
    """
    The key by which issue IDs are sorted.
    """
    # NOTE: This is written as separate function to guarantee that we keep the
    #       same sorting rule for both the raw issue-IDs and their
    #       corresponding links.
    return (item.source, item.id)


def format_issue_urls(
    log: ChangelogEntry, templates: Dict[str, str]
) -> Iterable[str]:
    """
    Extracts a list of URLs to issues from a changelog-entry.

    :param log: the changelog entry
    :param templates: A dictionary mapping an issue source to a string-template
        for the link. The value ``{id}`` is replaced with the issue-id.
    """
    for issue_id in sorted(log.issue_ids, key=_issue_id_sort_key):
        template = templates.get(issue_id.source, "")
        yield template.replace("{id}", str(issue_id.id))


def format_log(
    log: ChangelogEntry, issue_url_templates: Dict[str, str]
) -> Dict[str, Any]:
    """
    Convert a changelog-entry to a JSONifiable structure.
    """
    version = log.version or Version("0.0")
    return {
        "simple_version": (
            version.major,
            version.minor,
        ),
        "full_version": version.release,
        "is_highlight": log.is_highlight,
        "is_internal": log.is_internal,
        "issue_urls": list(format_issue_urls(log, issue_url_templates)),
        "detail": log.detail,
        "issue_ids": [
            item.id for item in sorted(log.issue_ids, key=_issue_id_sort_key)
        ],
        "subject": log.subject,
        "type": log.type_,
    }


class JSONRenderer:
    """
    Renders a changelog instance as JSON
    """

    # pylint: disable=too-few-public-methods

    FORMAT: ClassVar[str] = "json"

    def render(self, changelog: Changelog, file_metadata: FileMetadata) -> str:
        """
        Convert *changelog* into a JSON document.

        :param changelog: The changelog object
        :param issue_url_template: A simple string which is used to generate
            links to issues. The string ``{id}`` is replaced with the issue-id.
        """
        output: List[Dict[str, Any]] = []
        for release in changelog.releases:
            logs: List[Dict[str, Any]] = []
            for log in release.logs:
                logs.append(format_log(log, file_metadata.issue_url_templates))
            output.append(
                {
                    "logs": logs,
                    "meta": {
                        "date": release.release_date,
                        "notes": release.notes,
                        "version": release.version,
                    },
                }
            )
        return json.dumps(output, cls=CustomEncoder)
