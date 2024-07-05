"""
This module contains local exceptions for errors that are well-known in the
code-base of ``clproc``
"""


class ClprocException(Exception):
    """
    Base class for all clproc exceptions
    """


class ChangelogFormatError(ClprocException):
    """
    Exception which is raised when something is wrong in the "changelog.in"
    file.
    """


class ReleaseFormatError(ClprocException):
    """
    Exception which is raised whenever soemthing is wrong in the release-file
    """
