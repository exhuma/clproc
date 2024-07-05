"""
This module contains everything related to end-user reporting
"""

import logging

from clproc.model import ParsingIssueMessage

LOG = logging.getLogger(__name__)


def default_parse_issue_handler(msg: ParsingIssueMessage) -> None:
    """
    A simple handler for parsing issue which simply logs them using the logging
    framework.
    """
    LOG.log(level=msg.level, msg=msg.message)
