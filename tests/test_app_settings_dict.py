from app_settings_dict import Settings
from dataclasses import dataclass
from typing import Any
from typing import Tuple
import pytest
import re


def test_simple_settings() -> None:
    settings = Settings(
        settings_file_path="C:/Users/chris/Documents/sample_settings_file_name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        data={
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
        data={
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
    def sample_prompt_function(settings: Settings) -> Settings:
        # s = input("Enter the settings: ")
        return settings.update({"key1": "a", "key2": "b"})

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
        data={
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
    settings.clear()
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
        data={
            "key1": "hello",
        },
    )
    assert settings["key1"] == "hello"
    settings.clear()
    assert settings["key1"] == "value1"


def test_prompt() -> None:
    def sample_prompt_function() -> Any:
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
        data={
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
        data={
            "key1": "hello",
        },
    )
    assert settings["key1"] == "hello"
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "hello"
    settings["key1"] = "a"
    settings.load(fallback_option="default settings")
    assert settings["key1"] == "a"


def test_update() -> None:
    settings = Settings(
        settings_file_path="sample settings file name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        default_settings={
            "key1": [],
        },
        data={
            "key1": "hello",
        },
    )
    assert settings["key1"] == "hello"
    settings.update({"key1": "a"})
    assert settings["key1"] == "a"
    settings.update({"key2": "b"})
    assert settings["key2"] == "b"


def test_Settings__is_using_json() -> None:
    settings = Settings(
        settings_file_path="sample_settings_file_name.json",
        default_factories={
            "key1": lambda: "value1",
        },
        data={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings._Settings__is_using_json()
    settings.settings_file_path = "sample_settings_file_name.yaml"
    assert not settings._Settings__is_using_json()


def test_load_from_dict() -> None:
    settings = Settings()
    settings.load_from_dict(
        {
            "key1": "hello",
            "key2": "world",
        }
    )
    assert len(settings.data) == 0
    settings = Settings(
        data={
            "key1": "a",
            "key2": "b",
        }
    )
    settings.load_from_dict(
        {
            "key1": "c",
            "key2": "d",
        }
    )
    assert settings.data["key1"] == "c"
    assert settings.data["key2"] == "d"


def test_dump_to_dict() -> None:
    settings = Settings(
        settings_file_path="sample_settings_file_name.json",
        data={
            "key1": "hello",
            "key2": "world",
        },
    )
    assert settings.dump_to_dict() == {
        "key1": "hello",
        "key2": "world",
    }


def test_nested_Settings() -> None:
    settings = Settings(
        settings_file_path="sample_settings_file_name.json",
        default_settings={
            "key6": [],
            "key7": Settings(
                data={
                    "key8": "value8",
                }
            ),
        },
        data={
            "key1": "hello",
            "key2": "world",
            "key3": "value3",
            "key4": Settings(
                settings_file_path="why would anyone want an inner file though.yaml",
                data={
                    "key5": "value5",
                },
            ),
        },
    )
    assert settings.dump_to_dict() == {
        "key1": "hello",
        "key2": "world",
        "key3": "value3",
        "key4": {
            "key5": "value5",
        },
    }


def test_creating_setting_after_init() -> None:
    settings = Settings(
        settings_file_path="sample_settings_file_name.json",
        default_settings={
            "key1": [],
            "key2": "value2",
        },
    )
    with pytest.raises(KeyError):
        settings["key3"] = "value3"


def test_prompt_error() -> None:
    settings = Settings(
        settings_file_path="nonexistent file.json",
        default_settings={
            "key1": [],
            "key2": "value2",
        },
    )
    with pytest.raises(ValueError):
        settings.load(fallback_option="prompt user")


def test_nested_setting_loaders_and_dumpers() -> None:
    @dataclass
    class Coords:
        x: int
        y: int

        def __init__(self, x_and_y: Tuple[int, int]) -> None:
            self.x = x_and_y[0]
            self.y = x_and_y[1]

    settings = Settings(
        setting_loader=Coords,
        setting_dumper=lambda obj: (obj.x, obj.y),
        data={
            "location 1": Coords(x_and_y=(1, 2)),
            "location 2": Coords(x_and_y=(3, 4)),
            "patterns": Settings(
                setting_loader=re.compile,
                setting_dumper=lambda x: x.pattern,
                data={
                    "phone number pattern": re.compile(r"\d{3}-?\d{3}-?\d{4}"),
                    "email address pattern": re.compile(
                        r"[\w\d.+-]+@[\w\d.-]+\.[\w\d]+"
                    ),
                },
            ),
        },
    )
    settings_dict = settings.dump_to_dict()
    assert settings_dict["location 1"] == (1, 2)
    assert settings_dict["location 2"] == (3, 4)
    assert settings_dict["patterns"]["phone number pattern"] == r"\d{3}-?\d{3}-?\d{4}"
    assert (
        settings_dict["patterns"]["email address pattern"]
        == r"[\w\d.+-]+@[\w\d.-]+\.[\w\d]+"
    )
    settings.load_from_dict(settings_dict)
    assert settings["location 1"] == Coords(x_and_y=(1, 2))
    assert settings["location 2"] == Coords(x_and_y=(3, 4))
    assert settings["patterns"]["phone number pattern"] == re.compile(
        r"\d{3}-?\d{3}-?\d{4}"
    )
    assert settings["patterns"]["email address pattern"] == re.compile(
        r"[\w\d.+-]+@[\w\d.-]+\.[\w\d]+"
    )


def test_init_without_keywords() -> None:
    with pytest.raises(TypeError):
        Settings("sample settings file path.json")
