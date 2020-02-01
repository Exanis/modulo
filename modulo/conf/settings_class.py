from os import environ
from typing import Any, Optional
from importlib import import_module
from .exceptions import MissingConfigurationException, MissingConfigurationKeyException
from .env import env_bool, env_list


DEFAULT_SETTINGS = {
    'DEBUG': env_bool('DEBUG'),
    'CUSTOM_HANDLERS': {}
    'ROUTES': []
}


class Settings():
    def __init__(self: Settings, module: Optional[str] = None) -> None:
        if module is None:
            module = environ.get('MODULO_CONFIG_MODULE', None)
        if module is None:
            raise MissingConfigurationException('Missing configuration module. You must either set the MODULO_CONFIG_MODULE environment variable or pass it as a parameter to your settings instance.')
        try:
            self._original_values = import_module(module)
        except ModuleNotFoundError:
            raise MissingConfigurationException(f'Module {module} cannot be loaded.')
        self._values = {}

    def __getattr__(self: Settings, key: str) -> Any:
        if key not in self._values:
            try:
                self._values[key] = getattr(self.values, key)
            except AttributeError:
                if key in DEFAULT_SETTINGS:
                    self._values[key] = DEFAULT_SETTINGS[key]
                else:
                    raise AttributeError(f'Setting {key} is not defined and have no default value')
        return self._values[key]
