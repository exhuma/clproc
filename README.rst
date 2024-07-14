clproc
======

``clproc`` helps to provide human-readable and user-friendly change-logs for
projects without compromise on git-commit quality.

It uses a *separate* source for log-entries and is also usable for projects
that don't use git.


Why clproc?
-----------

``clproc`` does not depend on specially formatted git commit messages. This has
several *very* important consequences:

- It clearly separates developers from end-users

  - Developers don't need to worry about commit-message content leaking into
    end-user visible change-logs
  - End-Users will only see well-crafted, curated content for changes

- Changelogs are "just content" and they can be easily modified as time goes
  on.
- It is easy to modify old entries in the change-log witout rewriting the git
  history (f.ex. for clarifications and/or typos).

Example alternatives to ``clproc`` that rely on git log-messages:

- https://git-cliff.org/
- https://pypi.org/project/gitchangelog/


Release Information
~~~~~~~~~~~~~~~~~~~

``clproc`` also separates normal "change-log" entries from "release notes"
where "release notes" is prose aimed to explain details of a specific release.
Relase notes are optional and can be added on an "as-needed" basis.


Example Input File
------------------

::

  # -*- changelog-version: 2.0 -*-
  1.1         ; added   ; Added a new feature
  1.0.0       ; support ; Mark as final release
  1.0.0a2     ; fixed   ; Fixed something
  1.0.0a1     ; support ; Initial Development Release



pre-commit integration
----------------------

As of version 1.2.0, ``clproc`` can be integrated with pre-commit_. When using
with ``pre-commit`` the *expected* version will be auto-detected. At the time
of this writing, ``clproc`` supports only two metadata sources:

- A ``pyproject.toml`` file using setuptools_ as build-backend
- A ``package.json`` file for NPM packages
- A ``cargo.toml`` file for rust crates

The arguments ``--exact`` and ``--release-only`` are of primary interest. Using
"exact" checking, the changelog *must* contain an entry matching the version
number in the metadata file *exactly*. When using ``--release-only``, only the
"release-nodes" (see the docs for details) are checked, providing a more
lenient check.


Example pre-commit config:

.. code-block:: yaml


    ---
    repos:
      - repo: https://git.ptech.lu/connectivity-oss/software-development/clproc.git
        rev: v1.2.0
        hooks:
          - id: clproc
            args: ["--release-only"]


.. _pre-commit: https://pre-commit.com
.. _setuptools: https://setuptools.pypa.io
