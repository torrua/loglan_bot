"""Asynchronous HTTP Client for fetching and caching Loglan.org content"""

from __future__ import annotations

import time
from typing import NamedTuple

import aiohttp
from bs4 import BeautifulSoup

from app.logger import log

MAIN_SITE = "http://www.loglan.org/"
DEFAULT_USER_AGENT = "LoglanBot/0.2 (+https://github.com/torrua/loglan_bot)"
CACHE_TTL_SECONDS = 3600  # 1 hour cache


class CachedPage(NamedTuple):
    soup: BeautifulSoup
    timestamp: float


class LoglanSiteClient:
    """Async HTTP client for loglan.org with in-memory caching and timeout protection."""

    def __init__(self, base_url: str = MAIN_SITE, cache_ttl: int = CACHE_TTL_SECONDS):
        self.base_url = base_url
        self.cache_ttl = cache_ttl
        self._cache: dict[str, CachedPage] = {}
        self._timeout = aiohttp.ClientTimeout(total=10)

    async def get_soup(self, url: str) -> BeautifulSoup | None:
        """Fetches a URL and returns parsed BeautifulSoup or None on error."""
        now = time.time()
        if url in self._cache:
            cached = self._cache[url]
            if now - cached.timestamp < self.cache_ttl:
                log.debug("Serving URL from cache: %s", url)
                return cached.soup

        headers = {"User-Agent": DEFAULT_USER_AGENT}
        try:
            async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
                log.debug("Fetching external URL: %s", url)
                async with session.get(url) as response:
                    if response.status != 200:
                        log.error("Failed to fetch %s, status code: %d", url, response.status)
                        return None
                    raw_bytes = await response.read()
                    try:
                        html_content = raw_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        html_content = raw_bytes.decode("latin-1", errors="replace")

                    soup = BeautifulSoup(html_content, "lxml")
                    self._cache[url] = CachedPage(soup=soup, timestamp=now)
                    return soup
        except Exception as exc:
            log.error("Error while fetching/parsing %s: %s", url, exc)
            return None


site_client = LoglanSiteClient()
