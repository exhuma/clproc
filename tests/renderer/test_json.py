import random
from datetime import date
from json import dumps, loads
from typing import Any, Dict, List, Tuple, Union

import pytest
from packaging.version import Version

import clproc.renderer as renderer
from clproc.model import (
    Changelog,
    ChangelogEntry,
    ChangelogType,
    FileMetadata,
    IssueId,
)
from clproc.renderer.json import CustomEncoder, format_log


def _dict_getter(obj: Dict[str, Any], path: Tuple[Union[str, int], ...]) -> Any:
    """
    Retrieve a value from a dictionary using a specific path.

    The path ("foo", 0, "bar") takes the key "foo" from the root, and assuming
    that this is a list, then takes item at index 0. Then we assume that *that*
    item is another object and take the key "bar". This would match the
    following object and return ``10``::

        {
            "foo": [{"bar": 10}]
        }
    """
    node: Union[Dict[str, Any], List[Any]] = obj
    for key in path:
        if isinstance(node, dict) and isinstance(key, str):
            try:
                node = node[key]
            except KeyError as exc:
                raise KeyError(
                    f"Path {path} not applicable to {obj!r} "
                    f"(Key {key!r} not found in {node!r})"
                ) from exc
        elif isinstance(node, list) and isinstance(key, int):
            node = node[key]  # type: ignore
        else:
            raise TypeError(f"The path {path} cannot be applied to {obj!r}")
    return node


@pytest.mark.parametrize(
    "path, expected",
    [
        (("meta", "version"), "1.2"),
        (("meta", "date"), "2000-01-02"),
        (("meta", "notes"), "the-release-notes"),
        (("logs", 0, "simple_version"), [1, 2]),
        (("logs", 0, "full_version"), [1, 2, 3]),
        (("logs", 0, "is_highlight"), True),
        (("logs", 0, "is_internal"), True),
        (("logs", 0, "type"), "changed"),
        (("logs", 0, "subject"), "the-subject"),
        (("logs", 0, "issue_ids"), [1, 2]),
        (("logs", 0, "detail"), "the-detail"),
        (
            ("logs", 0, "issue_urls"),
            ["https://the-tracker/1", "https://the-tracker/2"],
        ),
    ],
)
def test_field_details(
    sample_log: Changelog, path: Tuple[Union[str, int], ...], expected: Any
):
    """
    Make sure the values in the JSON object have the correct value

    :param path: A tuple describing the path how to get to the value in question
        in the JSON tree.
    """
    instance = renderer.create("json")
    assert instance is not None
    output = instance.render(
        sample_log,
        FileMetadata(
            issue_url_templates={"default": "https://the-tracker/{id}"}
        ),
    )
    data = loads(output)
    # We pick the first release for validation (each release is rendered in the
    # same way)
    release = data[0]
    result = _dict_getter(release, path)
    assert result == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (Version("1.2.3"), '"1.2.3"'),
        (ChangelogType.ADDED, '"added"'),
        (date(2000, 1, 1), '"2000-01-01"'),
    ],
)
def test_json_converter(value: Any, expected: Any):
    """
    Ensure the JSON encoder is capable of rendering the internal custom objects
    """
    result = dumps(value, cls=CustomEncoder)
    assert result == expected


def test_json_converter_unknown():
    """
    Make sure we raise an appropriate type when we get an unencodable object
    """

    class UnknownType:
        pass

    with pytest.raises(TypeError):
        dumps(UnknownType(), cls=CustomEncoder)


@pytest.mark.parametrize("version", ["1.0", "2.0"])
def test_issue_urls_default(version: str, sample_log: Changelog):
    """
    Each issue ID should get its own URL rendered
    """

    instance = renderer.create("json")
    assert instance is not None
    output = instance.render(
        sample_log,
        FileMetadata(
            issue_url_templates={"default": "https://the-tracker/{id}"}
        ),
    )
    result = set(loads(output)[0]["logs"][0]["issue_urls"])
    assert result == {"https://the-tracker/1", "https://the-tracker/2"}


@pytest.mark.parametrize("version", ["1.0", "2.0"])
def test_issue_urls_multiple(version: str, sample_log: Changelog):
    """
    We should be able to specify more than one issue-url template
    """

    instance = renderer.create("json")
    assert instance is not None
    output = instance.render(
        sample_log,
        FileMetadata(
            issue_url_templates={
                "default": "https://the-tracker/{id}",
                "tpl2": "https://second-tracker/{id}",
            }
        ),
    )
    result = set(loads(output)[0]["logs"][0]["issue_urls"])
    assert result == {"https://the-tracker/1", "https://the-tracker/2"}


def test_issue_sorting():
    """
    We want the issue IDs and URLs in the JSON output to have the same
    ordering.

    This will allow "merging/zipping" of both lists for end-users.

    This is a documented feature and this test ensures we keep that behaviour.
    """
    ids = list(range(100))
    random.shuffle(ids)
    issues = [
        IssueId(id, random.choice(["foo", "bar", "default"])) for id in ids
    ]
    # Make sure that sorting also includes the source name
    issues.append(IssueId(issues[0].id, "aaaaaa"))
    issues.append(IssueId(issues[0].id, "zzzzzz"))

    item = ChangelogEntry(version=Version("1.0"), issue_ids=frozenset(issues))
    result = format_log(
        item,
        issue_url_templates={
            "default": "<default:{id}>",
            "foo": "<foo:{id}>",
            "bar": "<bar:{id}>",
            "aaaaaa": "<aaaaaa:{id}>",
            "zzzzzz": "<zzzzzz:{id}>",
        },
    )
    for id_, url in zip(result["issue_ids"], result["issue_urls"]):
        assert url.endswith(f":{id_}>")
