# pylint: skip-file
import clproc

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
project = "clproc"
copyright = "2022, Michel Albert"
author = "Michel Albert"
version = clproc.__version__
release = clproc.__exact_version__
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
todo_include_todos = False
html_static_path = ["_static"]
htmlhelp_basename = "clprocdoc"
latex_elements = {}

latex_documents = [
    (
        "index",
        "clproc.tex",
        "clproc Documentation",
        "Michel Albert",
        "manual",
    ),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
