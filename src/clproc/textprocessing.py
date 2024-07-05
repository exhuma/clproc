"""
This module contains helper functions for text manipulations.
"""
from textwrap import dedent


def get_multiline(raw_value: str, indent: str = "") -> str:
    """
    Cleans and reindents multiline text
    """
    raw_value = dedent(raw_value).strip()
    lines = raw_value.splitlines()
    output_lines = [(f"{indent}{line}").rstrip() for line in lines]
    return "\n".join(output_lines)
