Usage
=====

``clproc`` provides two subcommands. One for rendering the changelog, and one
for checking the changelog for consistency.

Refer to ``clpro --help`` for details.

Checking
--------

Checking is useful to integrate into CI pipelines to ensure that a release (see :ref:`releases`)
contains an appropriate changelog.

Check if a changelog contains information for release "1.0"::

    clproc <changelog-file> check 1.0

Check in "strict" mode (all warnings become errors)::

    clproc <changelog-file> check --strict 1.0

Help on the ``check`` command::

    clproc <changelog-file> check --help


Rendering
---------

Rendering is very similar to checking::

    clproc <changelog-file> render --format json

Help on the ``render`` command::

    clproc <changelog-file> render --help
