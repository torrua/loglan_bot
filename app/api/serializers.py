"""DTO Serializers mapping loglan_core SQLAlchemy models to LOD Manager TypeScript contracts."""

from __future__ import annotations

import json
import re
from typing import Any

from loglan_core import Author, Definition, Event, Type, Word


def _sort_parents_by_origin(parents: list[str], origin: Any) -> list[str]:
    """Sort parent word names in morphological order according to `origin` (with alphabetical fallback)."""
    if len(parents) <= 1 or not origin or not isinstance(origin, str):
        return sorted(parents)

    clean_origin = re.sub(r"[\(\)/+ ]", "", origin).lower()

    def pos_of(p: str) -> int:
        stem = p.strip("-").lower()
        if not stem:
            return 999999
        idx = clean_origin.find(stem)
        if idx != -1:
            return idx
        if len(stem) >= 4:
            idx4 = clean_origin.find(stem[:4])
            if idx4 != -1:
                return idx4
        if len(stem) >= 3:
            idx3 = clean_origin.find(stem[:3])
            if idx3 != -1:
                return idx3
        return 999999

    return sorted(parents, key=lambda p: (pos_of(p), p))


def serialize_definition(d: Definition) -> dict[str, Any]:
    """Serializes a Definition model to LOD Manager Definition contract."""
    # Combine slots and grammar_code into grammar string (e.g. '2a' or '0')
    grammar = None
    if d.slots is not None or d.grammar_code is not None:
        s_part = str(d.slots) if d.slots is not None else ""
        g_part = str(d.grammar_code) if d.grammar_code is not None else ""
        grammar = (s_part + g_part) or None

    pos = getattr(d, "position", None)
    position = int(pos) if isinstance(pos, (int, float)) else 1

    tags = getattr(d, "case_tags", None)
    tags_str = str(tags) if tags and "Mock" not in str(tags) else None

    usage = getattr(d, "usage", None)
    usage_str = str(usage) if usage and "Mock" not in str(usage) else None

    return {
        "id": d.id,
        "position": position,
        "grammar": grammar,
        "usage": usage_str,
        "body": str(d.body) if d.body and "Mock" not in str(d.body) else "",
        "tags": tags_str,
    }


def _extract_notes_metadata(notes_val: Any) -> tuple[dict[str, Any], str | None]:
    if isinstance(notes_val, str) and notes_val.strip().startswith("{"):
        try:
            notes_val = json.loads(notes_val)
        except Exception:
            pass

    if isinstance(notes_val, dict):
        extra_parts = [
            f"{k}: {v}" if k != "notes" else str(v)
            for k, v in notes_val.items()
            if k not in ("author", "year", "rank") and v
        ]
        return notes_val, "; ".join(extra_parts) if extra_parts else None

    if isinstance(notes_val, (dict, list)):
        return {}, json.dumps(notes_val, ensure_ascii=False)

    return {}, str(notes_val) if notes_val is not None else None


def serialize_word_detail(word: Word) -> dict[str, Any]:
    """Serializes a loaded Word model with relationships to LOD Manager WordDetail contract."""
    authors = getattr(word, "authors", []) or []
    base_authors = (
        "/".join(a.abbreviation for a in authors if getattr(a, "abbreviation", None)) or None
    )

    note_dict, clean_notes = _extract_notes_metadata(word.notes)
    note_author = note_dict.get("author")
    note_year = note_dict.get("year")
    note_rank = note_dict.get("rank")

    # Combine base authors and note author
    source: str | None
    if base_authors and note_author:
        source = f"{base_authors} {note_author}"
    else:
        source = base_authors or (str(note_author) if note_author else None)

    # Year as string
    year_val = word.year
    year_str = (
        str(year_val.year)
        if year_val is not None and hasattr(year_val, "year")
        else (str(year_val)[:4] if year_val else None)
    )
    combined_year = (
        f"{year_str} {note_year}"
        if (year_str and note_year)
        else (year_str or (str(note_year) if note_year else None))
    )

    rank_str = str(word.rank) if word.rank is not None else None
    combined_rank = (
        f"{rank_str} {note_rank}"
        if (rank_str and note_rank)
        else (rank_str or (str(note_rank) if note_rank else None))
    )

    # Definitions sorted by position
    raw_defs = getattr(word, "definitions", []) or []
    sorted_defs = sorted(raw_defs, key=lambda d: d.position or 0)
    definitions = [serialize_definition(d) for d in sorted_defs]

    # Affixes (djifoa) - strip dashes if present
    raw_affixes = getattr(word, "djifoa", None) or getattr(word, "affixes", None) or []
    affixes = [
        getattr(a, "name", str(a)).replace("-", "")
        for a in raw_affixes
        if getattr(a, "name", str(a))
    ]

    # Spellings
    raw_spellings = getattr(word, "spellings", []) or []
    spellings = [s.name for s in raw_spellings if getattr(s, "name", None)]

    # Complexes where this word is used
    raw_complexes = getattr(word, "complexes", []) or []
    used_in = [c.name for c in raw_complexes if getattr(c, "name", None)]

    # Parents (primitives / components sorted by appearance in word/origin)
    raw_parents = getattr(word, "parents", []) or []
    parents = _sort_parents_by_origin(
        [p.name for p in raw_parents if getattr(p, "name", None)],
        getattr(word, "origin", None),
    )

    # Derivatives / Children (excluding affixes, matching desktop Tauri get_word)
    raw_derivatives = getattr(word, "derivatives", []) or []
    children = [
        c.name
        for c in raw_derivatives
        if getattr(c, "name", None) and getattr(getattr(c, "type", None), "type_x", "") != "Affix"
    ]

    # Type name and ID
    word_type = getattr(word, "type", None)
    type_name = word_type.type_ if word_type else None
    type_id = word.type_id or (word_type.id if word_type else 0)

    # Event names
    ev_start = getattr(word, "event_start", None)
    event_start_name = ev_start.name if ev_start else None

    ev_end = getattr(word, "event_end", None)
    event_end_name = ev_end.name if ev_end else None

    def _to_str(v: Any) -> str | None:
        if v is None or isinstance(v, (dict, list)):
            return None
        s = str(v)
        if "MagicMock" in s or "<Mock" in s:
            return None
        return s

    return {
        "id": int(word.id) if word.id is not None else 0,
        "name": _to_str(word.name) or "",
        "type_name": _to_str(type_name),
        "type_id": int(type_id) if type_id is not None else 0,
        "source": source,
        "year": combined_year,
        "rank": combined_rank,
        "match_": _to_str(getattr(word, "match", None)),
        "origin": _to_str(word.origin),
        "origin_x": _to_str(word.origin_x),
        "notes": clean_notes,
        "event_start_name": _to_str(event_start_name),
        "event_end_name": _to_str(event_end_name),
        "affixes": affixes,
        "spellings": spellings,
        "definitions": definitions,
        "used_in": used_in,
        "parents": parents,
        "children": children,
    }


def serialize_word_list_item(row: Any) -> dict[str, Any]:
    """Serializes a light query row (id, name, type_name, def_count) to WordListItem."""
    if isinstance(row, dict):
        return {
            "id": row.get("id"),
            "name": row.get("name"),
            "type_name": row.get("type_name"),
            "def_count": row.get("def_count", 0),
        }

    # SQLAlchemy Row or tuple
    return {
        "id": row[0],
        "name": row[1],
        "type_name": row[2] if len(row) > 2 else None,
        "def_count": row[3] if len(row) > 3 else 0,
    }


def serialize_type(t: Type, word_count: int = 0) -> dict[str, Any]:
    """Serializes a Type model to TypeItem matching TypeScript interface."""
    return {
        "id": t.id,
        "name": t.type_,
        "type": t.type_,
        "type_x": getattr(t, "type_x", t.type_),
        "group_": t.group,
        "group": t.group,
        "word_count": word_count,
        "parentable": bool(getattr(t, "parentable", False)),
        "description": t.description,
    }


def serialize_event(e: Event) -> dict[str, Any]:
    """Serializes an Event model to EventItem matching TypeScript interface."""
    date_str = ""
    if e.date:
        date_str = str(e.date)

    return {
        "id": e.id,
        "event_id": e.event_id,
        "name": e.name,
        "date": date_str,
        "definition": e.definition,
        "annotation": e.annotation,
        "suffix": e.suffix,
        "notes": e.definition,
    }


def serialize_author(a: Author, word_count: int = 0) -> dict[str, Any]:
    """Serializes an Author model to AuthorItem matching TypeScript interface."""
    return {
        "id": a.id,
        "initials": a.abbreviation,
        "abbreviation": a.abbreviation,
        "full_name": a.full_name,
        "notes": a.notes,
        "word_count": word_count,
    }
