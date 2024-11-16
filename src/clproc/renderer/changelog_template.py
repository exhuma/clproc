"""
This module contains the definition of a renderer which transforms a changelog
object into a changelog-template (a "changelog.in") file.

The generated file will be sorted and aligned. This renderer was originally
created to auto-format "changelog.in" file.
"""

from typing import Any, ClassVar, Dict, Iterable, List
from itertools import zip_longest
from csv import writer
from io import StringIO

from packaging.version import Version

from clproc.model import Changelog, ChangelogEntry, FileMetadata, IssueId


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
) -> List[str]:
    """
    Convert a changelog-entry to a JSONifiable structure.
    """
    column_values: List[str] = []
    column_values.append(str(log.version))
    column_values.append(log.type_.value)
    column_values.append(log.subject)
    column_values.append(",".join(sorted(log.issue_ids)))
    column_values.append("i" if log.is_internal else " ")
    column_values.append("h" if log.is_highlight else " ")
    column_values.append(log.detail)
    return column_values


def padded(data: List[List[str]], *, inner="") -> List[List[str]]:
    """
    Create a copy of *data* with included padding.

    >>> padded(["a", "b", "c"], inner="---")
    ["a--", "---b---", "---c"]

    :param inner: The padding text that is added on the inside. The first and
        last value in the list will only have it applied to the end/front
        respectively.
    """
    first, *inner_values, last = data
    return (
        [
            f"{first.strip()}{inner}" if first.strip() else "",
        ]
        + [
            f"{inner}{value.strip()}{inner}" if value.strip() else ""
            for value in inner_values
        ]
        + [f"{inner}{last.strip()}" if last.strip() else ""]
    )


def aligned(data: List[List[str]]) -> List[List[str]]:
    column_widths = [0] * len(data[0])
    for row in data:
        for idx, cell in enumerate(row):
            if idx == len(column_widths):
                column_widths.append(len(cell))
            else:
                column_widths[idx] = max(len(cell), column_widths[idx])
    output = []
    for row in data:
        aligned_cells = [
            ("%%-%ds" % width) % value
            for value, width in zip_longest(row, column_widths, fillvalue="")
        ]
        output.append(aligned_cells)
    return output


class TemplateRenderer:
    """
    Renders a changelog instance as ".in" file
    """

    # pylint: disable=too-few-public-methods

    FORMAT: ClassVar[str] = "changelog-template"

    def render(self, changelog: Changelog, file_metadata: FileMetadata) -> str:
        """
        Convert *changelog* into a JSON document.

        :param changelog: The changelog object
        :param issue_url_template: A simple string which is used to generate
            links to issues. The string ``{id}`` is replaced with the issue-id.
        """
        logs: List[List[str]] = []
        for release in sorted(
            changelog.releases,
            key=lambda release: release.version,
            reverse=True,
        ):
            for log in sorted(
                release.logs, reverse=True, key=lambda log: log.version
            ):
                logs.append(
                    padded(
                        format_log(log, file_metadata.issue_url_templates),
                        inner=" ",
                    )
                )

        logs = aligned(logs)
        stream = StringIO()

        csv = writer(stream, dialect="clproc")
        csv.writerows(logs)
        return stream.getvalue()
