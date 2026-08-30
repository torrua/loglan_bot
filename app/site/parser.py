"""Structured Content Parser and HTML Sanitizer for Loglan.org Materials"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from app.site.client import MAIN_SITE

if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag

SECTION_ANCHORS: dict[str, list[str]] = {
    "articles": ["articles", "Articles"],
    "texts": ["texts", "Texts", "Sample Texts"],
    "columns": ["columns", "Columns", "Regular Columns from Lognet"],
}


@dataclass(frozen=True)
class ArticleMeta:
    """Metadata representing an article, text, or column."""

    title: str
    url: str
    raw_href: str
    author: str | None
    description: str
    section: str


class LoglanContentParser:
    """Parser and sanitizer for loglan.org structured content and articles."""

    @classmethod
    def parse_section(cls, soup: BeautifulSoup, section_key: str) -> list[ArticleMeta]:
        """Parses a section (articles, texts, columns) from the main page soup."""
        target_list = cls._find_section_list(soup, section_key)
        if not target_list:
            return []

        articles: list[ArticleMeta] = []
        for li in target_list.find_all("li", recursive=False):
            item = cls._parse_list_item(li, section_key)
            if item:
                articles.append(item)
        return articles

    @staticmethod
    def _find_section_list(soup: BeautifulSoup, section_key: str) -> Tag | None:
        """Locates the ordered or unordered list corresponding to a section."""
        names = SECTION_ANCHORS.get(section_key, [section_key])

        for name in names:
            anchor = soup.find("a", {"name": name})
            if anchor:
                parent_h2 = anchor.find_parent(["h2", "h3"])
                if parent_h2 and (next_list := parent_h2.find_next(["ol", "ul"])):
                    return next_list

        for h2 in soup.find_all(["h2", "h3"]):
            if any(k.lower() in h2.get_text().lower() for k in names):
                if next_list := h2.find_next(["ol", "ul"]):
                    return next_list
        return None

    @staticmethod
    def _parse_list_item(li: Tag, section_key: str) -> ArticleMeta | None:
        """Extracts article metadata from a single list item."""
        link = li.find("a")
        if not link or not link.get("href"):
            return None

        raw_href = str(link["href"]).strip()
        title = link.get_text().strip()
        if not title:
            return None

        full_text = li.get_text().replace(title, "").strip()
        full_text = re.sub(r"^[\s,.\-—:]+", "", full_text).strip()

        author = None
        description = full_text
        author_pattern = r"(?:,\s*)?by\s+([^,.\n]+(?:\s+[^,.\n]+)*)[.]?$"
        if author_match := re.search(author_pattern, full_text, re.IGNORECASE):
            author = author_match.group(1).strip()
            description = full_text[: author_match.start()].strip()
            description = re.sub(r"[\s,]+$", "", description)

        clean_href = raw_href.lstrip("/")
        return ArticleMeta(
            title=title,
            url=f"/site/{clean_href}",
            raw_href=raw_href,
            author=author,
            description=description or "Loglan reading material.",
            section=section_key,
        )

    @classmethod
    def clean_article_html(
        cls,
        soup: BeautifulSoup,
        section: str = "",
        current_article: str = "",
    ) -> tuple[str, str]:
        """Cleans, normalizes, and sanitizes an article HTML page.

        Returns (article_title, clean_html_body).
        """
        if not soup or not soup.body:
            return "Article", "<p>Article content could not be loaded.</p>"

        body = soup.body
        article_title = cls._extract_article_title(soup, body)

        cls._clean_boilerplate_and_tags(body)
        cls._normalize_links(body, section)
        cls._normalize_images(body, section)
        cls._enhance_elements(body)

        clean_html = "".join(str(child) for child in body.children if str(child).strip())
        return article_title, clean_html

    @staticmethod
    def _extract_article_title(soup: BeautifulSoup, body: Tag) -> str:
        """Extracts and removes the main heading from the body or title."""
        if body.h1:
            h1 = body.h1.extract()
            if text := h1.get_text().strip():
                return text
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return "Loglan Article"

    @staticmethod
    def _clean_boilerplate_and_tags(body: Tag) -> None:
        """Removes external archive disclaimer headers and unwanted tags."""
        for p in body.find_all(["p", "div"]):
            p_text = p.get_text().strip()
            if "A page from the" in p_text and "Loglan web site" in p_text:
                p.decompose()

        for tag in body.find_all(["script", "style", "iframe", "object", "embed", "applet"]):
            tag.decompose()

        obsolete_attrs = [
            "bgcolor",
            "text",
            "link",
            "vlink",
            "alink",
            "marginwidth",
            "marginheight",
            "border",
        ]
        for tag in body.find_all(True):
            for attr in obsolete_attrs:
                if attr in tag.attrs:
                    del tag.attrs[attr]

    @classmethod
    def _normalize_links(cls, body: Tag, section: str) -> None:
        """Normalizes external, internal, and relative links."""
        for a in body.find_all("a"):
            raw_href = a.get("href")
            if not raw_href or not isinstance(raw_href, str) or raw_href.startswith("#"):
                continue

            href = raw_href.strip()
            if href.startswith(("http://", "https://")):
                if re.match(r"^https?://(?:www\.)?loglan\.org/", href):
                    rel = re.sub(r"^https?://(?:www\.)?loglan\.org/", "", href)
                    a["href"] = f"/site/{rel}"
                else:
                    a["target"] = "_blank"
                    a["rel"] = "noopener noreferrer"
            else:
                a["href"] = cls._resolve_relative_link(href, section)

    @classmethod
    def _normalize_images(cls, body: Tag, section: str) -> None:
        """Ensures image sources point to valid URLs with modern classes."""
        for img in body.find_all("img"):
            raw_src = img.get("src")
            if raw_src and isinstance(raw_src, str):
                src = raw_src.strip()
                if not src.startswith("http"):
                    base = f"{MAIN_SITE}{section}/" if section else MAIN_SITE
                    img["src"] = urljoin(base, src)
            img["class"] = "img-fluid my-2 rounded shadow-sm"

    @staticmethod
    def _enhance_elements(body: Tag) -> None:
        """Applies responsive Bootstrap styling classes to tables and blockquotes."""
        for table in body.find_all("table"):
            table["class"] = "table table-hover table-bordered table-sm my-3 align-middle"

        for bq in body.find_all("blockquote"):
            bq["class"] = (
                "blockquote p-3 my-3 bg-light border-start border-3 border-primary rounded-end"
            )

    @staticmethod
    def _resolve_relative_link(href: str, current_section: str) -> str:
        """Resolves relative link to the correct /site/... path."""
        href = href.strip()
        if href.startswith("/"):
            return f"/site{href}"
        if href.startswith("../"):
            clean = href.replace("../", "")
            return f"/site/{clean}"
        if "/" not in href and current_section:
            return f"/site/{current_section}/{href}"
        return f"/site/{href}"
