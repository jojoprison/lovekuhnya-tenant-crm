import time
from collections.abc import Callable
from functools import wraps
from typing import Any

_cache: dict[str, tuple[Any, float]] = {}


def get(key: str) -> Any | None:
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None


def set(key: str, value: Any, ttl: int = 60) -> None:
    _cache[key] = (value, time.time() + ttl)


def delete(key: str) -> None:
    _cache.pop(key, None)


def clear() -> None:
    _cache.clear()


def cached(ttl: int = 60, key_prefix: str = "") -> Callable:
    """Decorator for caching funct results

    Usage:
        @cached(ttl=30, key_prefix="analytics")
        async def get_summary(org_id: int) -> dict:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            cached_value = get(cache_key)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator
