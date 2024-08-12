.. _release-files:

Release Files
=============

A "release file" contains an entry for detected releases. If the parser detects
a release, but it is missing in the release-file it will use sensible defaults
for that release.

The file is written using YAML becuase in this particular case, CSV would become
messy because one key use-case for release-files is to add multiline
release-notes.

Example:
--------

.. code-block:: yaml

    ---
    # The "meta" key is used internally to control how the release-file is to be
    # interpreted
    meta:
        # meta.version indicates that this is a release-file of a particular
        # version. Only 1.0 is supporte at the time of this writing.
        version: "1.0"

    # The "releases" key contains a mapping from release-versions to the
    # additional data. Each key of the mapping is the release version as string.
    releases:
        "2.1":
            # The date represents the point in time when the release was made.
            date: 2018-01-01
            # Notes can contain a multiline description for this particular
            # release.
            notes: |
                Hello World
                ===========

                This is an exmaple release description for release "2.1"
