import pytest
from clproc.renderer.changelog_template import padded


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
