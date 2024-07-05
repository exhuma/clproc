.. _releases:

Log Entries vs. Releases
========================

In addition to simple changelog "entries/rows/logs", ``clproc`` adds a level of
aggregation above: *Releases*

A "release" groups one or more log-entries and renders them inside that group.

This is intended to provide a more condensed output to end-users.


Release Detection
-----------------

A release "group" is detected by looking at the first *n* values of a version.
The default for *n* is 2 but can be modified via :ref:`file_metadata` lines.

With the default of *n=2*, the entries ``1.2.1``, ``1.2``, ``1.2.3.4.5`` are all
regrouped under the release ``1.2``.

For *CalVer* it is possible to set this value to *3* or *4* depending on
selected scheme. With *n=3*, all the following values will be detected as
separate release: ``2020.1.1``, ``2020.1.2``, ``2020.1.3``.
