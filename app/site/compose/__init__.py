# -*- coding: utf-8 -*-
"""
HTML Export extensions of LOD database models
"""

import os
from abc import ABC, abstractmethod

DEFAULT_HTML_STYLE = os.getenv("DEFAULT_HTML_STYLE", "ultra")


class Item(ABC):
    @abstractmethod
    def export_as_html(self) -> str:
        pass
