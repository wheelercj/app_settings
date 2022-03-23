import platform
if int(platform.python_version().split('.')[1]) < 8:
    from typing_extensions import Literal  # https://pypi.org/project/typing-extensions/
else:
    from typing import Literal
from typing import Dict, Callable, Any
import json
import yaml  # https://pypi.org/project/PyYAML/
from app_settings.defaults_dict import DefaultsDict


class Settings(DefaultsDict):
    def __init__(
        self,
        settings_file_path: str,
        prompt_user_for_all_settings: Callable[[], dict] = None,
        default_factories: Dict[Any, Callable[[], Any]] = None,
        default_settings: Dict[Any, Any] = None,
        dict_: dict = None,
        **kwargs: Any
    ) -> None:
        """Initializes the settings.

        Parameters
        ----------
        settings_file_path : str
            The absolute path to the settings file. Can be either a JSON or a
            YAML file.
        prompt_user_for_all_settings : Callable[[], dict], None
            A function that prompts the user to enter settings and returns
            them.
        default_factories : Dict[Any, Callable[[], Any]], None
            The dictionary of functions to call if keys are missing.
        default_settings : Dict[Any, Any], None
            The dictionary of default settings that do NOT initialize the
            dictionary, but instead are used by the reset method if and when a
            setting should be reset to its default. All items this class is
            initialized with are also saved in the default_settings dictionary,
            so default_settings is only helpful if a default setting should be
            saved for a key that is in default_factories. If a default setting
            and a default factory but not a starting item are provided for a
            key, the default factory is called.
        dict_ : dict, None
            The dictionary to initialize with. These items are saved in both
            the default_settings and the data dictionary.
        kwargs : Any
            The keyword arguments to initialize the dictionary with. These
            items are saved in both the default_settings and the data
            dictionary.
        """
        self.settings_file_path = settings_file_path
        self.prompt_user_for_all_settings = prompt_user_for_all_settings
        super().__init__(default_factories, dict_, **kwargs)
        if default_settings is None:
            default_settings = {}
        self.default_settings = default_settings
        for key, item in self.data.items():
            self.default_settings[key] = item

    def reset(self, key: Any) -> None:
        """Resets a setting to its default value.

        Raises KeyError if the key is not in the default settings.
        """
        self.data[key] = self.default_settings[key]

    def reset_all(self) -> None:
        """Resets all settings with default values to their default values."""
        for key in self.default_settings:
            self.reset(key)

    def save(self) -> None:
        """Saves the settings to the settings file."""
        with open(self.settings_file_path, "w", encoding="utf8") as file:
            if self.__is_using_json():
                json.dump(self.data, file, indent=4)
            else:
                yaml.dump(self.data, file)

    def load(
        self,
        fallback_option: Literal[
            "default settings", "prompt user"
        ] = "default settings",
    ) -> None:
        """Loads the user's settings from a file.

        The settings are retrieved from settings.json if the file exists and is
        not empty. Otherwise, they are retrieved directly from the user via a
        settings menu or from default settings in the code depending on the
        chosen fallback option.

        Parameters
        ----------
        fallback_option : str
            Whether to fall back to default settings or prompting the user to
            enter settings if the settings don't exist yet. The user can only
            be prompted to enter settings if a function for that was given upon
            class initialization.

        Raises
        ------
        ValueError
            If an invalid fallback option was chosen.
        """
        try:
            with open(self.settings_file_path, "r", encoding="utf8") as file:
                if self.__is_using_json():
                    loaded_settings = json.load(file)
                else:
                    loaded_settings = yaml.load(file, Loader=yaml.FullLoader)
            if not loaded_settings:
                raise FileNotFoundError
            self.data.update(loaded_settings)
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError):
            if fallback_option == "default settings":
                print("Unable to load the settings. Using default settings.")
                self.data.update(self.default_settings)
            elif self.prompt_user_for_all_settings and fallback_option == "prompt user":
                self.data.update(self.prompt_user_for_all_settings())
            else:
                raise ValueError(f"fallback_option must be either 'default settings' or 'prompt user', not '{fallback_option}'")

    def __is_using_json(self) -> bool:
        """Returns whether the settings file is a JSON file."""
        return self.settings_file_path.lower().endswith(".json")
