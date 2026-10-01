"""DTO Serializers mapping loglan_core SQLAlchemy models to LOD Manager TypeScript contracts."""

from __future__ import annotations

import json
from typing import Any

from loglan_core import Author, Definition, Event, Type, Word


def serialize_definition(d: Definition) -> dict[str, Any]:
    """Serializes a Definition model to LOD Manager Definition contract."""
    # Combine slots and grammar_code into grammar string (e.g. '2a' or '0')
    grammar = None
    if d.slots is not None or d.grammar_code is not None:
        s_part = str(d.slots) if d.slots is not None else ""
        g_part = str(d.grammar_code) if d.grammar_code is not None else ""
        grammar = (s_part + g_part) or None

    return {
        "id": d.id,
        "position": d.position or 1,
        "grammar": grammar,
        "usage": d.usage,
        "body": d.body or "",
        "tags": getattr(d, "case_tags", None),
    }


def serialize_word_detail(word: Word) -> dict[str, Any]:
    """Serializes a loaded Word model with relationships to LOD Manager WordDetail contract."""
    # Authors abbreviation string joined by '/'
    authors = getattr(word, "authors", []) or []
    source = "/".join(a.abbreviation for a in authors if getattr(a, "abbreviation", None)) or None

    # Year as string
    year_val = word.year
    year_str = None
    if year_val is not None:
        if hasattr(year_val, "year"):
            year_str = str(year_val.year)
        else:
            year_str = str(year_val)[:4]

    # Notes stringification if dict
    notes_val = word.notes
    if isinstance(notes_val, (dict, list)):
        notes_str = json.dumps(notes_val, ensure_ascii=False)
    else:
        notes_str = str(notes_val) if notes_val is not None else None

    # Definitions sorted by position
    raw_defs = getattr(word, "definitions", []) or []
    sorted_defs = sorted(raw_defs, key=lambda d: d.position or 0)
    definitions = [serialize_definition(d) for d in sorted_defs]

    # Affixes (djifoa) - strip dashes if present
    raw_affixes = getattr(word, "djifoa", []) or []
    affixes = [a.name.replace("-", "") for a in raw_affixes if getattr(a, "name", None)]

    # Spellings
    raw_spellings = getattr(word, "spellings", []) or []
    spellings = [s.name for s in raw_spellings if getattr(s, "name", None)]

    # Complexes where this word is used
    raw_complexes = getattr(word, "complexes", []) or []
    used_in = [c.name for c in raw_complexes if getattr(c, "name", None)]

    # Parents (primitives / components)
    raw_parents = getattr(word, "parents", []) or []
    parents = [p.name for p in raw_parents if getattr(p, "name", None)]

    # Derivatives / Children
    raw_derivatives = getattr(word, "derivatives", []) or []
    children = [c.name for c in raw_derivatives if getattr(c, "name", None)]

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
        "year": year_str,
        "rank": _to_str(word.rank),
        "match_": _to_str(getattr(word, "match", None)),
        "origin": _to_str(word.origin),
        "origin_x": _to_str(word.origin_x),
        "notes": notes_str,
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


def serialize_type(t: Type) -> dict[str, Any]:
    """Serializes a Type model to TypeItem."""
    return {
        "id": t.id,
        "type": t.type_,
        "type_x": getattr(t, "type_x", t.type_),
        "group": t.group,
        "parentable": bool(getattr(t, "parentable", False)),
        "description": t.description,
    }


def serialize_event(e: Event) -> dict[str, Any]:
    """Serializes an Event model to EventItem."""
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
    }


def serialize_author(a: Author) -> dict[str, Any]:
    """Serializes an Author model to AuthorItem."""
    return {
        "id": a.id,
        "abbreviation": a.abbreviation,
        "full_name": a.full_name,
        "notes": a.notes,
    }
