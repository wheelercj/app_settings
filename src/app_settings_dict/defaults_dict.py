from collections import UserDict
from typing import Dict, Callable, Any


class DefaultsDict(UserDict):
    """A dictionary that can have multiple default factories.

    The default factories are the functions used if a key is missing to
    generate values for those keys instead of raising KeyError. Unlike with
    Python's built-in defaultdict, these default factories must be paired with
    predefined keys. If a key is missing from both the dictionary and the
    default factories, KeyError is raised.
    """

    def __init__(
        self,
        default_factories: Dict[Any, Callable[[], Any]] = None,
        dict_: dict = None,
        **kwargs: Any
    ) -> None:
        """Initializes the dictionary.

        Parameters
        ----------
        default_factories : Dict[Any, Callable[[], Any]], None
            The dictionary of functions to call if keys are missing.
        dict_ : dict, None
            The dictionary to initialize with.
        kwargs : Any
            The keyword arguments to initialize the dictionary with.
        """
        if default_factories is None:
            default_factories = {}
        self.default_factories = default_factories
        super().__init__(dict_, **kwargs)

    def __missing__(self, key: str) -> None:
        self.data[key] = self.default_factories[key]()
        return self.data[key]