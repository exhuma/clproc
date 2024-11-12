import pytest
from clproc.renderer.changelog_template import aligned, padded


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
                ["foo  ", "bar  ", "    "],
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
                ["hello", "world", "   "],
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
