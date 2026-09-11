"""
Boilerplate and pattern for high-resilience catalog-backed streaming discovery feeds
(Featured Carousel & Popular Shelves) in FastAPI.

Solves:
1. Serial upstream HTTP search bottlenecks & WAF 412 rate-limiting.
2. Negative cache poisoning (caching empty list `[]` on upstream errors).
3. Blank homepages using 3-tier fallback (Catalog Store -> Last Known Good Snapshot -> Offline Seed).
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Global in-memory snapshots for Tier 2 fallback
_LAST_FEATURED_SNAPSHOT: List[Dict[str, Any]] = []
_LAST_POPULAR_SNAPSHOT: List[Dict[str, Any]] = []
_STALE_CATALOG_FALLBACK: Optional[Dict[str, Any]] = None

CATALOG_BUILD_LOCK = asyncio.Lock()

# Tier 3: Immutable Offline Seed (Emergency zero-fail safety net)
OFFLINE_SEED_ANIME: List[Dict[str, Any]] = [
    {
        "season_id": "37738",
        "title": "Jujutsu Kaisen",
        "cover": "https://pic.bstarstatic.com/ogv/121db5971bf9eec014b2d5f0fa4b1bbad386aa79.png",
        "rating": "9.8",
        "index_show": "Tamat (24 Episode)",
        "description": "Yuji Itadori menelan kutukan tingkat tinggi demi menyelamatkan temannya."
    },
    {
        "season_id": "37699",
        "title": "Demon Slayer: Kimetsu no Yaiba",
        "cover": "https://pic.bstarstatic.com/ogv/360a08e1d51a6697b0e527d78a8aa829038e1bdf.png",
        "rating": "9.8",
        "index_show": "Tamat",
        "description": "Perjalanan Tanjiro Kamado membasmi iblis dan mengembalikan adiknya."
    },
    {
        "season_id": "1004857",
        "title": "Solo Leveling",
        "cover": "https://pic.bstarstatic.com/ogv/0126786c558c42a22be220f1882d2bb4bf2ca3fe.png",
        "rating": "9.7",
        "index_show": "Diperbarui ke E12",
        "description": "Sung Jinwoo, hunter peringkat terlemah yang bangkit melalui sistem misterius."
    },
    {
        "season_id": "37719",
        "title": "Attack on Titan Final Season",
        "cover": "https://pic.bstarstatic.com/ogv/41eb63a233ec6e2e5052fa95521ae599187326b8.png",
        "rating": "9.9",
        "index_show": "Tamat",
        "description": "Pertarungan terakhir umat manusia melawan para titan dan takdir kebebasan."
    }
]


def set_cache_safe(key: str, val: Any, ttl: int = 3600, min_items: int = 1) -> bool:
    """
    Negative caching guardrail: Rejects saving empty or truncated list structures
    into the cache store, preventing cache poisoning from temporary upstream glitches.
    """
    if isinstance(val, (list, tuple)) and len(val) < min_items:
        logger.warning("Rejected caching empty/sub-threshold list for key '%s' (len=%d)", key, len(val))
        return False

    # Assuming set_cache() exists in the host application
    # set_cache(key, val, ttl=ttl)
    return True


def parse_rating_val(val: Any) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def parse_latest_rank(index_show: Any) -> tuple:
    s = str(index_show or '').lower()
    ep_match = re.search(r'e(\d+)', s)
    ep_num = int(ep_match.group(1)) if ep_match else 0
    status_score = 0
    if "segera diperbarui" in s:
        status_score = 1
    elif "diperbarui" in s:
        status_score = 2
    return (status_score, ep_num)


async def get_base_catalog_items(get_cache_fn, build_catalog_coro) -> List[Dict[str, Any]]:
    """
    Helper to safely retrieve or build in-memory catalog store with double-checked locking.
    """
    global _STALE_CATALOG_FALLBACK
    cached_store = get_cache_fn("catalog:full_store")
    if cached_store and cached_store.get("items"):
        return cached_store["items"]

    async with CATALOG_BUILD_LOCK:
        cached_store = get_cache_fn("catalog:full_store")
        if cached_store and cached_store.get("items"):
            return cached_store["items"]
        try:
            built = await build_catalog_coro()
            if built and built.get("items"):
                set_cache_safe("catalog:full_store", built, ttl=3600)
                _STALE_CATALOG_FALLBACK = built
                return built["items"]
        except Exception as e:
            logger.error("Failed building catalog in helper: %s", e)

    if _STALE_CATALOG_FALLBACK and _STALE_CATALOG_FALLBACK.get("items"):
        return _STALE_CATALOG_FALLBACK["items"]
    return []
