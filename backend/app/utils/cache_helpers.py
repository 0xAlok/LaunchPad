from ..extensions import cache


def get_cache_version(key):
    value = cache.get(key)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def bump_cache_version(key):
    cache.set(key, get_cache_version(key) + 1, timeout=0)
