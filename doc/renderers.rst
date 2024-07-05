Renderers
=========

``clproc`` uses a pluggable architecture for changlog renderers. While they are
not (yet) exposed as "real" plugins, the code-base allows for easy editing and
addition of existing/new renderers.

Currently, two renderers are supported:

* Markdown (intended audience = humans/end-users)

  Example usage::

      clproc changelog.in render -f md

* JSON (intended audience = machines)

  Example usage::

      clproc changelog.in render -f json

  One key feature of the JSON renderer is that the keys ``issue_ids`` and
  ``issue_urls`` guarantee identical ordering (Item 10 of ``issue_ids``
  corresponds to Item 10 of ``issue_urls``). This provides an easy access to
  the issue-id itself for clean rendering without needing to parse the URL.
