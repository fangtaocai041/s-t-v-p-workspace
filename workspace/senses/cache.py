"""SearchCache — 搜索缓存 (避免重复感知)"""

from __future__ import annotations
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import json
import hashlib


class SearchCache:
    """搜索缓存。
    
    缓存感受器的感知结果，减少对外部服务的重复查询。
    默认 TTL = 24 小时。
    """

    def __init__(self, ttl_hours: int = 24):
        self._cache: Dict[str, dict] = {}
        self._ttl = timedelta(hours=ttl_hours)

    def get(self, query: str, species: str = "") -> Optional[dict]:
        key = self._key(query, species)
        entry = self._cache.get(key)
        if entry is None:
            return None
        cached_time = datetime.fromisoformat(entry["cached_at"])
        if datetime.now() - cached_time > self._ttl:
            del self._cache[key]
            return None
        return entry["data"]

    def set(self, query: str, species: str, data: dict):
        key = self._key(query, species)
        self._cache[key] = {
            "data": data,
            "cached_at": datetime.now().isoformat(),
        }

    def _key(self, query: str, species: str) -> str:
        raw = f"{query}|{species}"
        return hashlib.md5(raw.encode()).hexdigest()

    def clear(self):
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)
