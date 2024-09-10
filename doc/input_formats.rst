.. _input_formats:

Input Formats
=============

At the time of this writing, ``clproc`` supports two major input formats. They
are identified by a comment-line including the changelgog version as
:ref:`file_metadata`.

If the line is *missing*, version 1.0 will be used as default for
backwards-compatibility.

Version 2.0
-----------

File Metadata::

    # -*- changelog-version: 2.0 -*-

CSV Columns
~~~~~~~~~~~

version
    A version compatible with :pep:`440` (See :ref:`design_decisions` for
    details on the choice of PEP-440)

type
    A changelog type following "Keep a Changelog"

    .. todo:: Mention "unreleased"

subject
    A short one-line description of the change (details can be added in the last
    column)

issue_ids
    A comma-separated list of Issue IDs which can be rendered as URLs using
    ``issue-url-template`` from the :ref:`file_metadata`

    When multiple templates are defined, the issue-ids can be prefixed with the
    template identifier. If no prefix is defined, the value ``default`` is
    assumed.

internal
    If this column is non-empty, the entry is marked as "internal"

highlight
    If this column is non-empty, the entry is marked as "highlight"

detail
    A more detailed description of the change in question. This can be a
    multiline markdown string, following the CSV RFC for multiline/quoted
    values: Start the value *immediately* after the field separator with a
    quote, and end the multiline-value with a second quote:

    .. code-block:: text

        first-line;second-col;"This is a
        multiline string
        and we're still in the last-column here"
        second-line; ...

Important changes to version 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **The special "release" lines are no longer supported**

  Releases are now specified in a "release-file". See :ref:`file_metadata`.

  This line caused inconsistencies in handling of input lines, was hard to read
  and rarely used. A separate release-file improves overall tidyness and
  simplicity for authoring.

* **Log entries no longer have timestamps associated to them**

  The dates on individual log-entries are ambiguous for both the author and
  end-user. The dates could mean any of the following points in time (non
  exhaustive):

  * when the application/library was released
  * when the commit was made
  * when the feature branch was integrated
  * (in the case of remote services) when the service was deployed
  * ...

  This ambiguity removes all value from that field.

  Dates now only exist on *releases*.

* **Dates no longer include time information**

  Time information is too granular and does not add any value. But it makes it
  more cumbersome for the changelog author. It was removed.

* **Links to issues are no longer hard-coded**

  As "internal-only" tool, the links to issue-trackers were hard-coded. This is
  now controlled via the ``issue-url-template`` setting. If URLs should be
  rendered, this setting is **required**. See :ref:`file_metadata`.

Version 1.0
-----------

File Metadata::

    # -*- changelog-version: 1.0 -*-

This is a legacy format and *should be considered deprecated*. It is still
supported to avoid rewriting old changelogs.

CSV Columns
~~~~~~~~~~~

version
    A version compatible with :pep:`440` (See :ref:`design_decisions` for
    details on the choice of PEP-440)

type
    A changelog type following "Keep a Changelog"

subject
    A short one-line description of the change (details can be added in the last
    column)

issue_ids
    A comma-separated list of Issue IDs which can be rendered as URLs using
    ``issue-url-template`` from the :ref:`file_metadata`

internal
    If this column is non-empty, the entry is marked as "internal"

highlight
    If this column is non-empty, the entry is marked as "highlight"

date
    A date/time timestamp for the log-entry formatted as
    ``YYYY-MM-DDTHH:MM[:SS]``

detail
    A more detailed description of the change in question. This can be a
    multiline markdown string, following the CSV RFC for multiline/quoted
    values: Start the value *immediately* after the field separator with a
    quote, and end the multiline-value with a second quote:

    .. code-block:: text

        first-line;second-col;"This is a
        multiline string
        and we're still in the last-column here"
        second-line; ...
