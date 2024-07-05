.. _file_metadata:

File Metadata
=============

Certain parsing aspects can be controlled using "file variables" (inspired by
`Emacs file variables`_).

Each variable is surrounded by ``-*-`` and should be on a single comment-line.
For example::


    # -*- variable-1: value-1 -*-
    # -*- variable-2: value-2 -*-
    # -*- variable-3: value-3 -*-

While they can appear anywhere in the file, it is recommended to keep these
variables at the top of the file.

.. _Emacs file variables: https://www.gnu.org/software/emacs/manual/html_node/emacs/Specifying-File-Variables.html#Specifying-File-Variables

Variables
---------

``changelog-version``
    Whether to use the ``1.0`` or ``2.0`` parser. It is **strongly** recommended
    to prefer ``2.0``. ``1.0`` exists only for backwards compatibility. Defaults
    to ``1.0`` if missing.

    Example::

        # -*- changelog-version: 2.0 -*-

``release-nodes``
    How many numbers of a version are used as "release" identifier. For example
    with ``release-nodes: 2`` the version ``1.2.3.4`` will be aggregated into
    release ``1.2``.

    Example::

        # -*- release-nodes: 2 -*-

``issue-url-template``

    A URL template that is provided to the renderers. It is used to provide
    links to specific issues listed in a changelog entry. The special value
    ``{id}`` will be replaced with the value taken from the ``issue_ids`` field
    in the input CSV file.

    Multiple templates are supported by adding a prefix (separated by a
    semilcolon). Those prefixes can then be used in the "issue-ids" column in
    the changelog entries (f.ex. ``my-prefix:1234``).

    If no prefix is specified, the value ``default`` is assumed.

    Example::

        # -*- issue-url-template: https://my-tracker.my.domain/{id} -*-
        # -*- issue-url-template: my-prefix;https://other-tracker/{id} -*-

``release-file``

    A file containing additional information for releases. See
    :ref:`release-files` for more infoamtion.

    Example::

        # -*- release-file: my-releases.yaml -*-
