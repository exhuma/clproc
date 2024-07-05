from datetime import date
from io import StringIO
from textwrap import dedent

import pytest
from packaging.version import Version

from clproc.parser import v1


def test_release_date_detection():
    """
    Changelog Version 1.0 should auto-detect the release-version from log-entry
    dates for backwards compatibility.
    """
    data = StringIO(
        dedent(
            """\
            2.1.0  ; added   ; hello world   ;    ; ;h;          ;
                   ; support ; goodbye world ;    ; ; ;2010-01-01 ;
                   ; support ; yargs         ;    ; ; ;2010-01-02;
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    release_data = v1.extract_release_information(data, None)
    assert release_data[Version("2.1")].date == date(2010, 1, 2)


@pytest.mark.parametrize(
    "datestring, expected", [("2010-01-02 09:55:56", date(2010, 1, 2))]
)
def test_drop_time_info(datestring: str, expected: date):
    """
    Version 1.0 allows to add time-information. This should be parseable, but
    ignored.
    """
    data = StringIO(
        dedent(
            f"""\
            2.1.0  ; added   ; hello world   ;    ; ;h;{datestring};
            """
        )
    )
    data.name = f"<StringIO from {__file__}>"
    release_data = v1.extract_release_information(data, None)
    assert release_data[Version("2.1")].date == expected
