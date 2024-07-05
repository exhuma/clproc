from datetime import date
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
from packaging.version import Version

import clproc.renderer as renderer
from clproc import parse
from clproc.model import Changelog, ChangelogEntry, FileMetadata, ReleaseEntry
from clproc.renderer.markdown import (
    MarkdownRenderer,
    date_string,
    format_detail,
    format_log,
)

DATA_DIR = Path(__file__).parent / "data"
TEST_DATA = (DATA_DIR / "changelog.in").read_text(encoding="utf8")


@pytest.mark.parametrize(
    "value, expected",
    [
        (date(2019, 10, 25), "2019-10-25"),
    ],
)
def test_date_string(value: Any, expected: str):
    """
    Make sure that our date-formatting works as expected
    """
    result = date_string(value, surround=("(", ")"))
    expected = f"({expected})"
    assert result == expected


def test_unreleased():
    """
    Entries marked as "unreleased" should be skipped.
    """
    data = StringIO(
        dedent(
            """\
    version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

    unreleased ; changed  ; Some unreleased change
    2.8.0.post1 ; changed  ; Post-Release Test
    """
        )
    )
    result = parse(data)
    log = result.changelog.releases[0].logs[0]
    formatted_log = format_log(log, "")
    assert formatted_log == "- Post-Release Test *@ 2.8.0.post1*"


def test_major_release_formatting():
    """
    A major relase should not contain the "@ <version>@ suffix in lines.
    """
    data = StringIO(
        dedent(
            """\
    version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

    2.8.0 ; changed  ; Post-Release Test
    """
        )
    )
    result = parse(data)
    log = result.changelog.releases[0].logs[0]
    formatted_log = format_log(log, "")
    assert formatted_log == "- Post-Release Test"


def test_minor_post_release_fmt():
    """
    A minor post relase should also contain the "@ <version>@ suffix in lines.
    """
    data = StringIO(
        dedent(
            """\
    version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

    2.8.0.post1 ; changed  ; Post-Release Test
    """
        )
    )
    result = parse(data)
    log = result.changelog.releases[0].logs[0]
    formatted_log = format_log(log, "")
    assert formatted_log == "- Post-Release Test *@ 2.8.0.post1*"


def test_patch_post_release():
    """
    Ensure that we allow "post" releases in the changelog
    """
    data = StringIO(
        dedent(
            """\
    version; type ; subject ; issue_ids ; internal ; highlight ; date ; detail

    2.8.1.post1 ; changed  ; Post-Release Test
    """
        )
    )
    result = parse(data)
    log = result.changelog.releases[0].logs[0]
    formatted_log = format_log(log, "")
    assert formatted_log == "- Post-Release Test *@ 2.8.1.post1*"


def test_multiline():
    """
    Detail should maintain the indentation of the document but should also
    properly indent it by 2 spaces to line up with the bulleted lists.
    """
    result = parse(
        StringIO(
            dedent(
                """\
        foo; bar
        2.7.0 ; added ; foo ;;;;;"
            Hello World!

                preformatted
                    text
        "
        """
            )
        )
    )
    instance = renderer.create("markdown")
    assert instance is not None
    output = instance.render(result.changelog, FileMetadata())
    expected = dedent(
        """\
        # Changelog


        ## Release 2.7

        ### Added
        - foo

          Hello World!

              preformatted
                  text

        """
    )
    assert output == expected


def test_multiline_2():
    """
    Make sure that multiline markdown is supported as well.
    """
    result = parse(
        StringIO(
            dedent(
                """\
        foo; bar
        1.1.0 ; added ; Subject ;;;;;"

            For convenience, a new operation has been added. This function silently runs
            a remote command, ignoring any non-success error code. This is very useful
            for running remote tests for file existence where you *expect* failures and
            want to inspect the `<result>.succeeded` or `<result>.failed` attributes.

            Example:

                result = irun('[ -f /file/to/test ]')
                if result.failed:
                    print ""Remote file did not exist""
                else:
                    print ""Remote file did exist""
            "
        """
            )
        )
    )
    instance = renderer.create("markdown")
    assert instance is not None
    output = instance.render(result.changelog, FileMetadata())
    expected = dedent(
        """\
        # Changelog


        ## Release 1.1

        ### Added
        - Subject

          For convenience, a new operation has been added. This function silently runs
          a remote command, ignoring any non-success error code. This is very useful
          for running remote tests for file existence where you *expect* failures and
          want to inspect the `<result>.succeeded` or `<result>.failed` attributes.

          Example:

              result = irun('[ -f /file/to/test ]')
              if result.failed:
                  print "Remote file did not exist"
              else:
                  print "Remote file did exist"

        """
    )
    assert output == expected


def test_format_highlight():
    """
    Highlights should have something in there to make them stand out
    """
    result = format_log(ChangelogEntry(Version("1.0"), is_highlight=True), {})
    assert "\u2606" in result


def test_release_header():
    """
    We want to see the release notes in the output
    """
    renderer = MarkdownRenderer()
    result = renderer.render(
        Changelog(
            (
                ReleaseEntry(
                    version=Version("1.2.3"),
                    release_date=date(2000, 1, 1),
                    notes="release-notes",
                ),
            )
        ),
        FileMetadata(),
    )
    assert "1.2.3" in result
    assert "2000-01-01" in result
    assert "release-notes" in result


@pytest.mark.parametrize("version", ["1.0", "2.0"])
def test_issue_urls(version: str, sample_log: Changelog):
    """
    Each issue ID should get its own URL rendered
    """
    renderer = MarkdownRenderer()
    result = renderer.render(
        sample_log,
        FileMetadata(
            issue_url_templates={"default": "https://the-tracker/{id}"}
        ),
    )
    assert "https://the-tracker/1" in result
    assert "https://the-tracker/2" in result


def test_issues_without_link_template(sample_log: Changelog):
    """
    We want to be able to render the links, even if we have no link template
    """
    renderer = MarkdownRenderer()
    result = renderer.render(sample_log, FileMetadata())
    assert "#1, #2" in result


def test_format_empty_detail():
    """
    If a detail is empty, we should render an empty string
    """
    result = format_detail(ChangelogEntry(Version("1.0")))
    assert result == ""
