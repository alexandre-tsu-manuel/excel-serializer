import os

import pytest

import excel_serializer as es


def test_excel_serializer():
    data = {
        "foo": [
            {"name": "bar", "num": 42, "nums": [1, 2, 3]},
            {"name": "baz", "num": 1337, "nums": [4, 5, 6]},
        ],
        "bar": "baz",
        "baz": 42.1,
        "qux": {"foo": "bar", "baz": "qux"},
        "quux": [{"foo": "bar"}, {"baz": "qux"}],
    }

    es.dump(data, "test.xlsx")
    loaded_data = es.load("test.xlsx")
    assert loaded_data == data
    os.remove("test.xlsx")
