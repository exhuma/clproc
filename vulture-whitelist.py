"""
This module is used as a "whitelist" for "vulture". It serves no "application
logic" purpose. See the "vulture" docs on more details on this.
"""
# pylint: disable=pointless-statement, invalid-name

from clproc import cli, model

cli.main

model.ChangelogType.ADDED
model.ChangelogType.CHANGED
model.ChangelogType.SECURITY
model.ChangelogType.DEPRECATED
model.ChangelogType.REMOVED
model.ChangelogType.SUPPORT
model.ChangelogType.FIXED
model.ChangelogType.DOC
