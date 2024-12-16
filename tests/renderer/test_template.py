from io import StringIO

import pytest

from clproc.renderer.changelog_template import CustomWriter, aligned, padded


@pytest.mark.parametrize(
    "values, expected",
    [
        (
            [
                ["foo", "bar", "baz"],
                ["hello", "world", "john"],
            ],
            [
                ["foo  ", "bar  ", "baz "],
                ["hello", "world", "john"],
            ],
        ),
        (
            [
                ["foo", "bar"],
                ["hello", "world", "john"],
            ],
            [
                ["foo  ", "bar  "],
                ["hello", "world", "john"],
            ],
        ),
        (
            [
                ["foo", "bar", "baz"],
                ["hello", "world"],
            ],
            [
                ["foo  ", "bar  ", "baz"],
                ["hello", "world"],
            ],
        ),
        (
            [
                ["# comment should not affect length"],
                ["foo", "bar", "baz"],
                ["hello", "world"],
            ],
            [
                ["# comment should not affect length"],
                ["foo  ", "bar  ", "baz"],
                ["hello", "world"],
            ],
        ),
    ],
)
def test_aligned_cells(values, expected):
    """
    Ensure that we have a function that can align strings horizontally
    """
    result = aligned(values)
    assert result == expected


@pytest.mark.parametrize(
    "values, expected",
    [
        (
            ["", "foo", ""],
            ["", " foo ", ""],
        ),
        (
            ["foo", "bar", "baz"],
            ["foo ", " bar ", " baz"],
        ),
    ],
)
def test_padded_cells(values, expected):
    """
    Ensure that we have a function that can add padding to cells
    """
    result = padded(values, inner=" ")
    assert result == expected


@pytest.mark.parametrize(
    "rows, expected",
    [
        ([["foo"], ["   "], ["bar"]], ["foo", "", "bar"]),
        ([["foo"], [""], ["bar"]], ["foo", "", "bar"]),
    ],
)
def test_writer_empty_rows(rows, expected):
    """
    We don't want the default CSV behaviour of quoting empty rows.

    This test ensures that lines that are empty or contain whitespace only
    are rendered as a single empty line in the output.
    """

    stream = StringIO()
    writer = CustomWriter(stream, "excel")
    writer.writerows(rows)
    result = stream.getvalue().splitlines()
    assert result == expected


@pytest.mark.parametrize(
    "rows, expected",
    [
        ([[""]], []),
        ([["   "]], []),
        ([[""]] * 3, []),
        ([["   "]] * 3, []),
        ([["foo"], [""]], ["foo"]),
        ([["bar"], ["   "]], ["bar"]),
        ([["foo"], [""], ["   "], [""]], ["foo"]),
        ([["bar"], ["   "], [""], ["   "]], ["bar"]),
    ],
)
def test_writer_last_line(rows, expected):
    """
    If the end of the file contains empty-lines, do not output those.
    """

    stream = StringIO()
    writer = CustomWriter(stream, "excel")
    writer.writerows(rows)
    result = stream.getvalue().splitlines()
    assert result == expected
