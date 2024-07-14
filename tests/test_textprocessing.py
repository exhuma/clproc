"""
Unit tests for the clproc.textprocessing module
"""

from clproc.textprocessing import get_multiline


def test_get_multiline() -> None:
    """
    Ensure values are correctly wrapped and dedented.
    """
    mldata = (
        "\n"
        "    This taskl sets up inotify watches and reruns tests automatically if files\n"
        "    change. This uses `pytest-cache` instead of `pytest-xdist` to rerun only\n"
        "    failed tests. It also automatically generates coverage reports.\n"
        "    "
    )
    expected = (
        "This taskl sets up inotify watches and reruns tests automatically if files\n"
        "change. This uses `pytest-cache` instead of `pytest-xdist` to rerun only\n"
        "failed tests. It also automatically generates coverage reports."
    )
    result = get_multiline(mldata)
    assert result == expected
