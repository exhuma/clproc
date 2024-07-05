import clproc.renderer.base as base


def test_no_matching_format():
    """
    A non-existing format should not crash the app, but should return "None"
    """
    result = base.create("this-format-does-not-exist")
    assert result is None
