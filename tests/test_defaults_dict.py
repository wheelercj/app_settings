from app_settings_dict.defaults_dict import DefaultsDict
import pytest


def test_simple_items() -> None:
    default_values = {"key1": "hello", "key2": "world"}
    defaults_dict = DefaultsDict(data=default_values)
    assert defaults_dict["key1"] == "hello"
    assert defaults_dict["key2"] == "world"


def test_simple_factories() -> None:
    def example_function() -> str:
        # word = input('Enter a word: ')
        word = "something"
        return word

    default_factories = {
        "key1": lambda: "value1",
        "key2": lambda: [],
        "key3": example_function,
    }
    defaults_dict = DefaultsDict(default_factories)
    assert defaults_dict["key1"] == "value1"
    assert defaults_dict["key2"] == []
    assert defaults_dict["key3"] == "something"


def test_nonexistent_key() -> None:
    default_factories = {"key1": lambda: "value1"}
    default_values = {"key1": "hello", "key2": "world"}
    defaults_dict = DefaultsDict(default_factories, default_values)
    with pytest.raises(KeyError):
        defaults_dict["key82798"]


def test_items_and_factories() -> None:
    default_factories = {
        "key1": lambda: "value1",
        "key2": lambda: "value2",
        "key3": lambda: [],
    }
    default_values = {"key1": "hello", "key2": "world"}
    defaults_dict = DefaultsDict(default_factories, default_values)
    assert defaults_dict["key1"] == "hello"
    assert defaults_dict["key2"] == "world"
    assert defaults_dict["key3"] == []
    with pytest.raises(KeyError):
        defaults_dict["key82798"]


def test_deleted_items() -> None:
    default_factories = {"key1": lambda: "value1"}
    default_values = {"key1": "hello", "key2": "world"}
    defaults_dict = DefaultsDict(default_factories, default_values)
    assert defaults_dict["key1"] == "hello"
    assert defaults_dict["key2"] == "world"
    del defaults_dict["key1"]
    del defaults_dict["key2"]
    assert "key1" not in defaults_dict
    assert "key2" not in defaults_dict
    assert defaults_dict["key1"] == "value1"
    with pytest.raises(KeyError):
        defaults_dict["key2"]


def test_other_types() -> None:
    default_factories = {382782: lambda: "value1"}
    default_values = {4.5: "hello", True: lambda: lambda: "what"}
    defaults_dict = DefaultsDict(default_factories, default_values)
    assert defaults_dict[382782] == "value1"
    assert defaults_dict[4.5] == "hello"
    assert defaults_dict[True]()() == "what"


def test_reassigned_key() -> None:
    default_factories = {"key1": lambda: "value1"}
    default_values = {"key1": "hello", "key2": "world"}
    defaults_dict = DefaultsDict(default_factories, default_values)
    assert defaults_dict["key1"] == "hello"
    assert defaults_dict["key2"] == "world"
    defaults_dict["key1"] = "something"
    assert defaults_dict["key1"] == "something"
    assert defaults_dict["key2"] == "world"
