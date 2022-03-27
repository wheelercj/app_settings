import platform

if int(platform.python_version().split(".")[1]) < 8:
    from typing_extensions import Literal  # https://pypi.org/project/typing-extensions/
else:
    from typing import Literal
from typing import Dict, Callable, Any
import json
import yaml  # https://pypi.org/project/PyYAML/
from app_settings_dict.defaults_dict import DefaultsDict


class Settings(DefaultsDict):
    def __init__(
        self,
        settings_file_path: str = None,
        prompt_user_for_all_settings: Callable[["Settings"], "Settings"] = None,
        default_factories: Dict[Any, Callable[[], Any]] = None,
        default_settings: Dict[Any, Any] = None,
        data: dict = None,
        prevent_new_settings: bool = True,
        # setting_loader: Callable[[str], Any] = None,
        # setting_dumper: Callable[[Any], str] = None,
    ) -> None:
        """Initializes the settings.

        Parameters
        ----------
        settings_file_path : str, None
            The absolute path to the settings file. Can be either a JSON or a
            YAML file.
        prompt_user_for_all_settings : Callable[[Settings], Settings], None
            A function that prompts the user to enter settings and returns
            them. The argument is the current settings.
        default_factories : Dict[Any, Callable[[], Any]], None
            The dictionary of functions to call if keys are missing. Each of
            these functions must return the value for the given key (not the
            setting dictionary item).
        default_settings : Dict[Any, Any], None
            The dictionary of default settings that do NOT initialize the
            dictionary, but instead are used by a reset method if and when a
            setting should be reset to its default. The data this class is
            initialized with is also saved in the default_settings dictionary,
            so default_settings is usually only used when either the ``reset``
            method or the ``reset_all`` method is called. If a default setting
            and a default factory but not a starting item are provided for a
            key, the default factory is called.
        data : dict, None
            The dictionary to initialize with. These items are saved in both
            the default settings and in the data attribute without overwriting
            any existing default settings.
        prevent_new_settings : bool
            Whether or not to prevent new settings from being added to the
            settings dictionary after this class' initialization.
        """
        # setting_loader : Callable[[str], Any], None
        #     A function that loads a setting from a string. This function will
        #     be called on each and every setting when they are loaded from the
        #     settings file.
        # setting_dumper : Callable[[Any], str], None
        #     A function that dumps a setting to a string. This function will be
        #     called on each and every setting when they are saved to the
        #     settings file.
        self.settings_file_path = settings_file_path
        self.prompt_user_for_all_settings = prompt_user_for_all_settings
        self.prevent_new_settings = prevent_new_settings
        self.data = data or {}
        self.default_factories = default_factories or {}
        self.default_settings = default_settings or {}
        self.__create_defaults_from_data()
        # self.setting_loader = setting_loader
        # self.setting_dumper = setting_dumper

    def __create_defaults_from_data(self) -> None:
        """Creates default settings from the data dictionary."""
        for key, value in self.data.items():
            if key not in self.default_settings:
                self.default_settings[key] = value

    def __setitem__(self, key: Any, item: Any) -> None:
        if self.prevent_new_settings and key not in self.data:
            raise KeyError(
                f'"{key}" is not a valid setting. You can set '
                "prevent_new_settings to False in the Settings constructor call "
                "to allow new settings to be created after initialization."
            )
        super().__setitem__(key, item)

    def update(self, data: dict) -> None:
        """Updates the settings with the given dictionary.

        This update method cannot receive keyword arguments like the normal
        dict update method can because the normal update method uses
        ``self[key] = other[key]``, which can raise KeyError from this class's
        ``__setitem__`` method at times when it shouldn't.
        """
        self.data.update(data)

    def reset(self, key: Any) -> None:
        """Resets a setting to its default value.

        Raises KeyError if the key is not in the default settings.
        """
        self.data[key] = self.default_settings[key]

    def reset_all(self) -> None:
        """Resets all settings with default values to their default values."""
        for key in self.default_settings:
            self.reset(key)

    def prompt(self, key: Any) -> None:
        """Calls the default factory for a setting."""
        self.data[key] = self.default_factories[key]()

    def save(self) -> None:
        """Saves the settings to the settings file."""
        dict_ = self.dump_to_dict()
        with open(self.settings_file_path, "w", encoding="utf8") as file:
            if self.__is_using_json():
                json.dump(dict_, file, indent=4)
            else:
                yaml.dump(dict_, file)

    def load(
        self,
        fallback_option: Literal[
            "default settings", "prompt user"
        ] = "default settings",
        overwrite_existing_settings: bool = True,
    ) -> None:
        """Loads the user's settings from a file.

        The settings are retrieved from the settings file if the file exists
        and is not empty. Otherwise, they are retrieved directly from the user
        via a settings menu or from default settings in the code depending on
        the chosen fallback option. Any settings in the settings file whose
        keys are not in any of the dictionaries in Settings are ignored.

        Parameters
        ----------
        fallback_option : str
            Whether to fall back to default settings or prompting the user to
            enter settings if the settings don't exist yet. The user can only
            be prompted to enter settings if a function for that was given upon
            class initialization. If the fallback to default settings is used,
            only default settings that do not overwrite any current settings
            are used.
        overwrite_existing_settings : bool
            Whether to overwrite existing settings with the settings from the
            settings file. This option is ignored if a fallback option is used;
            using default settings never overwrites existing settings (only
            adding new ones that don't yet exist), and prompting the user to
            enter settings always overwrites existing settings (without
            deleting any that are not overwritten).

        Raises
        ------
        ValueError
            If an invalid fallback option was chosen.
        """
        try:
            with open(self.settings_file_path, "r", encoding="utf8") as file:
                if self.__is_using_json():
                    loaded_settings_dict = json.load(file)
                else:
                    loaded_settings_dict = yaml.load(file, Loader=yaml.FullLoader)
            if not loaded_settings_dict:
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError):
            print("Unable to load the settings.")
            if fallback_option == "default settings":
                print("Using default settings.")
                for key, value in self.default_settings.items():
                    if key not in self.data:
                        self.data[key] = value
            elif fallback_option == "prompt user":
                if self.prompt_user_for_all_settings is None:
                    raise ValueError(
                        "A function for prompting the user for settings was "
                        "not given upon class initialization."
                    )
                self = self.prompt_user_for_all_settings(self)
            else:
                raise ValueError(
                    "fallback_option must be either 'default settings' or "
                    f"'prompt user', not '{fallback_option}'"
                )
        else:
            self = self.load_from_dict(loaded_settings_dict)
            for key, value in self.data.items():
                if (
                    key in self.data
                    and overwrite_existing_settings
                    or (
                        key not in self.data
                        and (
                            key in self.default_settings
                            or key in self.default_factories
                        )
                    )
                ):
                    self.data[key] = value

    def dump_to_dict(self) -> dict:
        """Converts part of this Settings object to a normal dictionary.

        Only the data and default_settings attributes will be kept, but they
        can contain Settings objects that will also be converted to
        dictionaries recursively matching the same description.
        """
        settings_dict = {
            "is_app_settings_dict": True,
            "data": self.data,
            "default_settings": self.default_settings,
        }
        for key, value in settings_dict["data"].items():
            if isinstance(value, Settings):
                settings_dict["data"][key] = value.dump_to_dict()
        for key, value in settings_dict["default_settings"].items():
            if isinstance(value, Settings):
                settings_dict["default_settings"][key] = value.dump_to_dict()
        return settings_dict

    def load_from_dict(self, dict_: dict) -> "Settings":
        """Converts a normal dictionary with specific keys to a Settings object.

        Parameters
        ----------
        dict_ : dict
            The dictionary to convert. The dictionary must have the keys
            "is_app_settings_dict", "data", and "default_settings". The values
            paired with the keys "data" and "default_settings" must be
            dictionaries, and can contain dictionaries recursively matching the
            same description.

        Raises
        ------
        ValueError
            If the dictionary does not have the required keys. The value paired
            with the "is_app_settings_dict" key can be anything.
        """
        if (
            "is_app_settings_dict" not in dict_
            or "data" not in dict_
            or "default_settings" not in dict_
        ):
            raise ValueError(
                "The dictionary must have the keys 'is_app_settings_dict', "
                "'data', and 'default_settings'."
            )
        settings = Settings(
            settings_file_path=self.settings_file_path,
            prompt_user_for_all_settings=self.prompt_user_for_all_settings,
            prevent_new_settings=self.prevent_new_settings,
            data=self.data,
            default_factories=self.default_factories,
            default_settings=self.default_settings,
            # setting_loader=self.setting_loader,
            # setting_dumper=self.setting_dumper,
        )
        for key in ("data", "default_settings"):
            for k, v in dict_[key].items():
                if isinstance(v, dict) and "is_app_settings_dict" in v:
                    dict_[key][k] = self.load_from_dict(v)
            setattr(settings, key, dict_[key])
        return settings

    def __is_using_json(self) -> bool:
        """Returns whether the settings file is a JSON file."""
        return self.settings_file_path.lower().endswith(".json")
