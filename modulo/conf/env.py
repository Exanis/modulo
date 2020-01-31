def from_env(key: str, default: Any = None, allow_missing: bool = True) -> str:
    if not allow_missing and key not in environ:
        raise MissingConfigurationKeyException(key)
    return environ.get(key, default)


def env_bool(key: str, default: bool = False, allow_missing: bool = True) -> bool:
    value = from_env(key, default=default, allow_missing=allow_missing)
    if not value or value.lower() in ['0', 'false', 'off', 'no']:
        return False
    return True


def env_int(key: str, default: int = 0, allow_missing: bool = True) -> int:
    value = from_env(key, default=default, allow_missing=allow_missing)
    return int(value)


def env_list(key, default: list = [], allow_missing: bool = True) -> List[str]:
    value = from_env(key, default=','.join(default), allow_missing=allow_missing)
    return value.split(',')


def env_str(key, default: str = '', allow_missing: bool = True) -> str:
    return from_env(key, default=default, allow_missing=allow_missing)
