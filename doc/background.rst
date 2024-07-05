Background, Implementation & History
====================================

.. _design_decisions:

Drivers & Design Decisions
--------------------------

Having a Markdown and JSON format provides changelogs for both human- and
machine-consumption.

It was initially inspired by `keep a changelog`_ and has three main drivers:

* strictness (with a well-defined data-model) for machine consumption
* developer-comfort when authoring the changelog
* end-user (non-developers) friendly output

To achieve a balance between all three, the changelog uses a "parse & render"
approach:

* The developer writes a simplified changelog as CSV file
* clproc *parses* the CSV file into a well-defined (yet internal) data-format.
  This makes addition of new (or modification of existing) renderers easy.
* It then *renders* into a target output format. This format can be arbitrarily
  complex for both machine- and human-consumption. Keeping that complexity in
  the renderers, authoring of the changelog remains simple & easy.

PEP-440 as Version Parser
~~~~~~~~~~~~~~~~~~~~~~~~~

:pep:`440` was chosen as a versioning scheme because it is a superset of
"semantic versioning".

This means, if your project uses "Semantic Versioning" the values will be
properly parsed and accepted. But :pep:`440` brings additional useful concepts:

* *explicit* alpha-, beta- and release-candidate versions
* *explicit* pre- and post-releases
* epochs *((useful when the versioning scheme changes duringthe lifetime of a
  project, for example switching from CalVer to SemVer and still keep
  ordering).*

See the PEP for details on those concepts

.. _keep a changelog: https://keepachangelog.com/en/1.0.0/


CSV as Input Format
-------------------

CSV was chosen as input format as it provided the simplest "human-interface" for
developers. It is simple, easy to write and understand.

Other choices were rejected:

* **JSON**

  JSON contains too many special characters (curly braces, brackets), forces
  quotes everywhere and does not allow for comments. It is also necessary to
  repeat the key-names of the fields for each entry.

* **YAML**

  While YAML does not require as many special characters and quoting, it still
  suffers from repeated keys which makes it very cumbersome to write.

  It also suffers from unpredictable type-conversions for people less
  experiences in YAML.

* **XML**

  All the brackets and repeating tag-names would make this a nightmare as input
  format for changelogs.

* **Plain Text** (with custom parser)

  Plain text is too flexible and parsing it invites too many unknowns and
  unnecessary maintenance complexity.


Previous Efforts
----------------

``clproc`` is the result of many years of keeping changelogs internally at POST
Luxembourg. The code-base has been extracted from an internal housekeeping tool
for Python projects.

With the first release of ``clproc`` it is now also possible to use it for
non-Python projects.

To avoid rewriting old changelogs, a new file metadata system was introduced
inspired by `Emacs style file variables`_. Most notably, *new* changelogs
(starting with the first release of ``clproc``) should include the line to
enable the new & simplified parser::

    # -*- changelog-version: 2.0 -*-

See :ref:`file_metadata` and :ref:`input_formats` for more on metadata.

.. _Emacs style file variables: https://www.gnu.org/software/emacs/manual/html_node/emacs/Specifying-File-Variables.html#Specifying-File-Variables
