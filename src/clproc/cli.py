"""
The CLI interface
"""
import logging
import sys
from argparse import ArgumentParser, FileType, Namespace
from os.path import abspath
from typing import Callable, Optional, Sequence

from packaging.version import Version

from clproc import core
from clproc.discovery import discover_version
from clproc.exc import ClprocException

LOG = logging.getLogger(__name__)


def format_converter(fmt: str) -> str:
    """
    Provide abbreviations for formats
    """
    if fmt == "md":
        return "markdown"
    return fmt


def add_check_args(parser: ArgumentParser) -> None:
    """
    Add common CLI arguments for the "check/autocheck" subcommand.
    """
    parser.add_argument(
        "--strict",
        action="store_true",
        help=("Consider even the smallest issues in the changelog as error"),
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help=(
            "Check the version to the letter. Don't simplify it to the "
            "nearest release"
        ),
    )
    parser.add_argument(
        "--release-only",
        action="store_true",
        help=(
            "Consider only the release-version of the 'wanted' version. "
            "For example, running clproc in this mode, requesting "
            "v1.2.3.4rc1 will only check for the presence of v1.2 "
            "(depending on release-nodes defined in changelog.in)"
        ),
    )

def add_format_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--backup",
        "-b",
        action="store_true",
        help="Keep a backup file.",
        default=False
    )
    parser.add_argument(
        "--output",
        "-o",
        default="",
        help=(
            "Destination file. By default it writes back to the same file. "
            "Use '-' to write to stdout"
        )
    )

def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    """
    Process and parse command-line arguments and return the processes object.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (can be specified multiple times)",
    )
    parser.add_argument(
        "infile",
        help="The source-file for the changelog",
        type=FileType("r"),
    )
    subp = parser.add_subparsers()

    render_parser = subp.add_parser("render")
    render_parser.add_argument(
        "-n",
        "--num-releases",
        type=int,
        help=(
            "Only render the last N releases. Use 0 (default) "
            "to render all releases"
        ),
        metavar="N",
        default=0,
    )
    render_parser.add_argument(
        "-f",
        "--format",
        default="json",
        type=format_converter,
        help="the possible output format",
        choices=["md", "markdown", "json"],
    )
    render_parser.add_argument(
        "-o",
        "--outfile",
        default="-",
        help="Output file. Leave empty or set to '-' to use stdout",
    )
    render_parser.set_defaults(func=execute_render)

    check_parser = subp.add_parser("check")
    add_check_args(check_parser)
    check_parser.add_argument(
        "require_release",
        type=Version,
        metavar="VERSION",
        help=(
            "Ensure the changelog file contains a *release* entry "
            "for this version"
        ),
    )
    check_parser.set_defaults(func=execute_check)

    autocheck_parser = subp.add_parser("autocheck")
    add_check_args(autocheck_parser)
    autocheck_parser.set_defaults(func=execute_autocheck)

    format_parser = subp.add_parser(
        "format",
        help="Automatically format the '.in' file"
    )
    add_format_args(format_parser)
    format_parser.set_defaults(func=execute_format)

    output = parser.parse_args(args)
    if not hasattr(output, "func"):
        parser.error("Missing subcommand")
    return output


def setup_logging(verbosity: int = 0) -> None:
    """
    Configure logging for the application

    :param verbosity: How verbose should we be? The larger the value, the more
        output will be seen on the console.
    """
    if verbosity > 0:
        logging.basicConfig(level=logging.DEBUG)


def execute_render(namespace: Namespace) -> int:
    """
    Main entry-point for the "render" subcommand.

    :param namespace: The argparse namespace.
    :returns: A valid posix exit-code
    """
    LOG.info("Rendering %s", abspath(namespace.infile.name))
    render_output = core.make_changelog(
        fmt=namespace.format,
        infile=namespace.infile,
        num_releases=namespace.num_releases,
    )
    if namespace.outfile.strip() in {"-", ""}:
        print(render_output)
    else:
        with open(namespace.outfile.strip(), "w") as stream:
            print(render_output, file=stream)
    return 0


def execute_check(namespace: Namespace) -> int:
    """
    Main entry-point for the "check" subcommand.

    :param namespace: The argparse namespace.
    :returns: A valid posix exit-code
    """
    LOG.info("Checking %s", abspath(namespace.infile.name))
    expected_version = namespace.require_release
    return _execute_check_internal(namespace, expected_version)


def execute_autocheck(namespace: Namespace) -> int:
    """
    Main entry-point for the "autocheck" subcommand.

    :param namespace: The argparse namespace.
    :returns: A valid posix exit-code
    """
    LOG.info("Checking %s", abspath(namespace.infile.name))
    expected_version = Version(discover_version())
    return _execute_check_internal(namespace, expected_version)

def execute_format(namespace: Namespace) -> int:
    """
    Main entry-point for the "format" subcommand.

    :param namespace: The argparse namespace.
    :returns: A valid posix exit-code
    """
    LOG.info("Formatting %s", abspath(namespace.infile.name))
    core.format(
        infile=namespace.infile,
        output=namespace.output,
        backup=namespace.backup
    )
    return 0


def _execute_check_internal(
    namespace: Namespace, expected_version: Version
) -> int:
    check_output = core.check_changelog(
        expected_version,
        infile=namespace.infile,
        strict=namespace.strict,
        exact=namespace.exact,
        release_only=namespace.release_only,
    )
    if check_output:
        LOG.info("No issues found.")
        return 0
    print(
        (
            f"Version {expected_version} "
            f"not found in {abspath(namespace.infile.name)}"
        ),
        file=sys.stderr,
    )
    print(f"Errors found in {abspath(namespace.infile.name)}", file=sys.stderr)
    return 1


def main(args: Optional[Sequence[str]] = None) -> int:
    """
    Main entry-point the the CLI of clproc
    """
    namespace = parse_args(args)
    setup_logging(namespace.verbose)
    try:
        func: Callable[..., int] = namespace.func
        return func(namespace)
    except ClprocException as exc:
        LOG.debug(str(exc), exc_info=True)
        LOG.error("Error: %s", exc)
        return 1
