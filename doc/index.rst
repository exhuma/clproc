clproc
======

``clproc`` is a development housekeeping tool for changelogs.

It converts a well-defined CSV file into different formats. Primarily, a
markdown and JSON format. It is internally structured to easily support new
formats.

Topics
======

.. toctree::
    :maxdepth: 1

    changelog
    usage
    background
    log_vs_releases
    input_formats
    file_metadata
    release_files
    renderers
    API <api/modules>

Example
=======

Input (simple)
--------------

See :ref:`input_formats` for advanced examples.

.. code-block:: text
  :caption: changelog.in

  # -*- changelog-version: 2.0 -*-
  1.1         ; added   ; Added a new feature
  1.0.0       ; support ; Mark as final release
  1.0.0a2     ; fixed   ; Fixed something
  1.0.0a1     ; support ; Initial Development Release

Rendering
---------

.. code-block:: bash
  :caption: command

  clproc changelog.in render -f md

.. code-block:: markdown
  :caption: output

  # Changelog

  ## Release 1.1

  ### Added
  - Added a new feature

  ## Release 1.0

  ### Support
  - Mark as final release
  - Initial Development Release *@ 1.0.0a1*

  ### Fixed
  - Fixed something *@ 1.0.0a2*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
