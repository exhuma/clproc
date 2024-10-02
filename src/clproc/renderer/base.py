"""
This module contains the main entry-point for renderer instantiation.

It contains the factory function :py:func:`~.create` to get a reference to a
renderer.
"""

from typing import ClassVar, List, Optional, Protocol, Type

from clproc.model import Changelog, FileMetadata

from .changelog_template import TemplateRenderer
from .json import JSONRenderer
from .markdown import MarkdownRenderer


def create(format_: str) -> Optional["Renderer"]:
    """
    Instantiates the appropriate renderer
    """
    renderers: List[Type[Renderer]] = [
        JSONRenderer,
        MarkdownRenderer,
        TemplateRenderer,
    ]
    for cls in renderers:
        if cls.FORMAT == format_:
            return cls()
    return None


class Renderer(Protocol):
    """
    Superclass for changelog renderers.

    To instantiate a particular renderer, use::

        >>> from clproc.renderer import create
        >>> create('markdown')  # MarkdownRenderer
        >>> create('json')  # JSONRenderer
    """

    FORMAT: ClassVar[str]

    def render(
        self, changelog: Changelog, file_metadata: FileMetadata
    ) -> str:  # pragma: no cover
        """
        Render the given changelog and return the resulting data
        """
        ...
