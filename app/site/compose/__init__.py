"""
HTML Export extensions of LOD database models
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.config import settings

DEFAULT_HTML_STYLE = settings.default_html_style


class Item(ABC):
    """Abstract base class for HTML-rendered dictionary items."""

    @abstractmethod
    def export_as_html(self) -> str:
        """Render the item as an HTML string."""
        pass
