import pytest
from app_settings_dict import Settings


def test_simple_settings() -> None:
    settings = Settings(
        settings_file_path="C:/Users/chris/Documents/sample_settings_file_name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        dict_={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings["key1"] == "hello"
    assert settings["key2"] == "world"
    del settings["key1"]
    del settings["key2"]
    assert "key1" not in settings
    assert "key2" not in settings
    assert settings["key1"] == "value1"
    with pytest.raises(KeyError):
        settings["key2"]


def test_default_settings() -> None:
    settings = Settings(
        settings_file_path="sample settings file name.json",
        default_factories={
            "key1": lambda: "value1",
            "key2": lambda: "value2",
            "key3": lambda: "value3",
        },
        default_settings={
            "key3": [],
        },
        dict_={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings["key1"] == "hello"
    assert settings["key2"] == "world"
    assert settings["key3"] == "value3"
    del settings["key3"]
    assert settings["key3"] == "value3"
    settings.reset("key3")
    assert settings["key3"] == []
    settings["key3"] = "something"
    assert settings["key3"] == "something"
    settings.reset_all()
    assert settings["key1"] == "hello"
    assert settings["key2"] == "world"
    assert settings["key3"] == []


def test_load_without_file() -> None:
    def sample_prompt_function() -> dict:
        # s = input("Enter the settings: ")
        return {"key1": "a", "key2": "b"}

    settings = Settings(
        settings_file_path="not a real file.yaml",
        prompt_user_for_all_settings=sample_prompt_function,
        default_factories={
            "key1": lambda: "value1",
            "key2": lambda: "value2",
            "key3": lambda: "value3",
        },
        default_settings={
            "key3": [],
            "key4": "value4",
        },
        dict_={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings["key1"] == "hello"
    assert settings["key2"] == "world"
    assert settings["key3"] == "value3"
    settings.load(fallback_option="prompt user")
    assert settings["key1"] == "a"
    assert settings["key2"] == "b"
    assert settings["key3"] == "value3"
    with pytest.raises(KeyError):
        settings["key4"]
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "a"
    assert settings["key2"] == "b"
    assert settings["key3"] == "value3"
    assert settings["key4"] == "value4"
    settings.empty()
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "hello"
    assert settings["key2"] == "world"
    assert settings["key3"] == []
    assert settings["key4"] == "value4"
    with pytest.raises(ValueError):
        settings.load(fallback_option="invalid option")


def test_load_after_empty() -> None:
    settings = Settings(
        settings_file_path="sample settings file name.json",
        prompt_user_for_all_settings=lambda: 1 / 0,
        default_factories={
            "key1": lambda: "value1",
        },
        default_settings={
            "key1": [],
        },
        dict_={
            "key1": "hello",
        },
    )
    assert settings["key1"] == "hello"
    settings.empty()
    assert settings["key1"] == "value1"


def test_prompt() -> None:
    def sample_prompt_function() -> dict:
        # s = input("Enter a setting: ")
        return "a"

    settings = Settings(
        settings_file_path="sample settings file name.json",
        prompt_user_for_all_settings=lambda: {"key1": "a", "key2": "b"},
        default_factories={
            "key1": sample_prompt_function,
            "key2": lambda: "value2",
            "key3": lambda: "value3",
        },
        default_settings={
            "key3": [],
        },
        dict_={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings["key1"] == "hello"
    settings.prompt("key1")
    assert settings["key1"] == "a"


def test_changing_settings_before_load() -> None:
    settings = Settings(
        settings_file_path="sample settings file name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        default_settings={
            "key1": [],
        },
        dict_={
            "key1": "hello",
        },
    )
    assert settings["key1"] == "hello"
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "hello"
    settings["key1"] = "a"
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "a"


def test_Settings__is_using_json() -> None:
    settings = Settings(
        settings_file_path="sample_settings_file_name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        dict_={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings._Settings__is_using_json()
    settings.settings_file_path = "sample_settings_file_name.yaml"
    assert not settings._Settings__is_using_json()
