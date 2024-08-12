"""
This module defines a renderer to convert a changelog object into a markdown
document.
"""

from datetime import date
from io import StringIO
from textwrap import indent, wrap
from typing import ClassVar, Dict, List, Optional, TextIO, Tuple

from packaging.version import Version

from clproc.model import (
    Changelog,
    ChangelogEntry,
    ChangelogType,
    FileMetadata,
    ReleaseEntry,
)


def is_initial_release(version: Version) -> bool:
    """
    Returns True if a version is considered an initial relase for the version.
    This is false for "pre" and "post" releases. An "inital" release is the
    first release of that version that hit the prod.
    """
    return not (
        version.is_prerelease or version.is_postrelease or version.is_devrelease
    )


def date_string(
    date_value: Optional[date], surround: Tuple[str, str] = (" (", ")")
) -> str:
    """
    Convert a date into a human-readable string. *surround* can be a 2-tuple
    which will be used to surround the generated string.
    """
    if date_value:
        fmt = "%Y-%m-%d"
        fmt = f"{surround[0]}{fmt}{surround[1]}"
        datestring = date_value.strftime(fmt)
    else:
        datestring = ""
    return datestring


def format_detail(log: ChangelogEntry) -> str:
    """
    Returns a formatted "detail" section.
    """
    if log.detail.strip() == "":
        return ""
    return f"\n{indent(log.detail, '  ')}\n"


def format_log(log: ChangelogEntry, issue_url_templates: Dict[str, str]) -> str:
    """
    Wraps a single log-entry to 70 characters and prefixes it as a bulleted
    list.
    """
    issue_links: List[str] = []
    for issue_id in sorted(log.issue_ids, key=lambda item: item.id):
        issue_url_template = issue_url_templates.get(issue_id.source, "")
        if issue_url_template:
            url = issue_url_template.replace("{id}", str(issue_id.id))
            issue_links.append(f"[#{issue_id.id}]({url})")
        else:
            issue_links.append(f"#{issue_id.id}")

    issue_text = ""
    if log.issue_ids:
        issue_text = f" ({', '.join(issue_links)})"

    # return subjects of highlights as bold text
    if log.is_highlight:
        subject = f"\u2606 **{log.subject}**"
    else:
        subject = log.subject

    if is_initial_release(log.version):
        patch_version = ""
    else:
        patch_version = f" *@ {log.version}*"

    output = f"{subject}{patch_version}{issue_text}"

    tmp_output = wrap(
        output,
        initial_indent="- ",
        subsequent_indent="  ",
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(tmp_output)


def release_header(release: ReleaseEntry, data: TextIO) -> None:
    """
    Print a release header into *data*
    """
    version = str(release.version)
    print("", file=data)
    print(
        f"## Release {version}{date_string(release.release_date)}",
        file=data,
    )
    lines = (
        [""]
        + wrap(
            release.notes,
            drop_whitespace=False,
            replace_whitespace=False,
        )
        + [""]
    )
    if release.notes:
        print("\n".join(lines), file=data)


def section_header(log: ChangelogEntry, data: TextIO) -> None:
    """
    Print a section header into *data*
    """
    print("", file=data)
    print(f"### {log.type_.value.capitalize()}", file=data)


class MarkdownRenderer:
    """
    Renders a changelog instance as markdown
    """

    FORMAT: ClassVar[str] = "markdown"

    def render(self, changelog: Changelog, file_metadata: FileMetadata) -> str:
        """
        Convert *changelog* into a Markdown document.

        :param changelog: The changelog object
        :param issue_url_template: A simple string which is used to generate
            links to issues. The string ``{id}`` is replaced with the issue-id.
        """
        data = StringIO()
        releases = sorted(changelog.releases)

        print("# Changelog\n", file=data)

        for release in reversed(releases):
            logs = sorted(
                release.logs,
                key=lambda x: (
                    -list(ChangelogType).index(x.type_),
                    x.is_highlight,
                    x.version,
                ),
            )
            release_header(release, data)
            current_section = None
            for log in reversed(logs):
                if log.type_ != current_section:
                    section_header(log, data)
                    current_section = log.type_
                print(
                    format_log(log, file_metadata.issue_url_templates),
                    file=data,
                )
                if log.detail:
                    print(format_detail(log), file=data)
        return data.getvalue()
