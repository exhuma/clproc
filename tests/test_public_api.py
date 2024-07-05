"""
This file contains example unit-tests using pytest and classical unit-tests.
"""
from pathlib import Path

from clproc import ParseResult, parse

DATA_DIR = Path(__file__).parent / "data"


def test_simple_parsing() -> None:
    """
    We want a dead-simple programmatic entry-point
    """
    with (DATA_DIR / "changelog.in").open(encoding="utf8") as data:
        result = parse(data)
    assert isinstance(result, ParseResult)
