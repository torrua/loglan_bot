"""REST API route handlers for LOD Manager Telegram Mini App and Web."""

from __future__ import annotations

import datetime
import re
from typing import Any

from loglan_core import Author, BaseSelector, Definition, Event, Key, Setting, Type, Word
from quart import g, jsonify, request
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.engine import async_session_maker
from app.services.dictionary import DictionaryService

from . import api_bp
from .auth import optional_auth, require_admin
from .serializers import (
    serialize_author,
    serialize_event,
    serialize_type,
    serialize_word_detail,
    serialize_word_list_item,
)


def split_grammar(g_val: str | None) -> tuple[int | None, str | None]:
    """Split grammar string like '2a' into (slots=2, grammar_code='a')."""
    if not g_val or not str(g_val).strip():
        return None, None
    raw = str(g_val).strip()
    digits = []
    i = 0
    while i < len(raw) and raw[i].isdigit():
        digits.append(raw[i])
        i += 1
    slots = int("".join(digits)) if digits else None
    code = raw[i:].strip() or None
    return slots, code


def parse_year(year_val: Any) -> datetime.date | None:
    """Parse string/int year into date object."""
    if not year_val:
        return None
    y_str = str(year_val).strip()
    if y_str.startswith("'") and len(y_str) == 3 and y_str[1:].isdigit():
        yy = int(y_str[1:])
        full_y = 1900 + yy if yy >= 50 else 2000 + yy
        return datetime.date(full_y, 1, 1)
    if y_str.isdigit() and len(y_str) == 4:
        return datetime.date(int(y_str), 1, 1)
    if len(y_str) >= 10:
        try:
            return datetime.date.fromisoformat(y_str[:10])
        except ValueError:
            return None
    return None


# ─── Health check ─────────────────────────────────────────────────────────────
@api_bp.route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "app": "Loglan Dictionary API"})


# ─── Auth / Current User ──────────────────────────────────────────────────────
@api_bp.route("/auth/me", methods=["GET"])
@optional_auth
async def get_current_user():
    """Retrieve current user authentication details and admin status."""
    return jsonify(
        {
            "is_admin": getattr(g, "is_admin", False),
            "user": getattr(g, "tma_user", None),
        }
    )


# ─── Words List ───────────────────────────────────────────────────────────────
@api_bp.route("/words", methods=["GET"])
@optional_auth
async def get_words():
    """
    List words matching optional query filters with ETag caching support.
    Query parameters:
      - q: word name prefix or wildcard (* / ?)
      - typeFilter: type name or '__g__' prefixed group
      - eventId: event ID filter
      - limit: max words to return (default: 12000)
      - offset: pagination offset (default: 0)
    """
    q_str = request.args.get("q", "").strip()
    type_filter = request.args.get("typeFilter", "").strip()
    event_id_raw = request.args.get("eventId")
    limit = min(int(request.args.get("limit", 12000)), 25000)
    offset = max(int(request.args.get("offset", 0)), 0)

    event_id: int | None = None
    if event_id_raw and event_id_raw.lower() not in ("null", "none"):
        try:
            event_id = int(event_id_raw)
        except ValueError:
            pass

    async with async_session_maker() as session:
        # Base query with definition count aggregation
        query = (
            select(
                Word.id,
                Word.name,
                Type.type_.label("type_name"),
                func.count(Definition.id).label("def_count"),
            )
            .outerjoin(Type, Word.type_id == Type.id)
            .outerjoin(Definition, Definition.word_id == Word.id)
            .group_by(Word.id, Word.name, Type.type_, Word.event_end_id)
        )

        if q_str:
            if "*" in q_str or "?" in q_str:
                like_pat = q_str.lower().replace("*", "%").replace("?", "_")
                query = query.where(func.lower(Word.name).like(like_pat))
            else:
                query = query.where(func.lower(Word.name).like(f"{q_str.lower()}%"))

        if type_filter:
            if type_filter.startswith("__g__"):
                group_name = type_filter[5:]
                query = query.where(Type.group == group_name)
            else:
                query = query.where(Type.type_ == type_filter)

        if event_id is not None:
            # Resolve canonical event_id if id was passed
            ev = await session.get(Event, event_id)
            target_ev = ev.event_id if ev else event_id

            query = query.where(
                (Word.event_start_id.is_(None) | (Word.event_start_id <= target_ev))
                & (Word.event_end_id.is_(None) | (Word.event_end_id > target_ev))
            )

        # Ordering matching Rust backend: alphabetical by name, active words first
        query = (
            query.order_by(
                func.lower(Word.name),
                func.coalesce(Word.event_end_id, 0).asc(),
                Word.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(query)
        rows = result.all()
        items = [serialize_word_list_item(r) for r in rows]

        # Compute simple ETag from count and params
        etag_val = f'"w-{len(items)}-ev{event_id}"'
        if_none_match = request.headers.get("If-None-Match")
        if if_none_match and if_none_match == etag_val and not q_str and not type_filter:
            return "", 304

        response = jsonify(items)
        response.headers["ETag"] = etag_val
        return response


# ─── Word Detail ──────────────────────────────────────────────────────────────
@api_bp.route("/words/<int:word_id>", methods=["GET"])
@optional_auth
async def get_word_detail(word_id: int):
    """Retrieve complete word details including definitions, affixes, and relationships."""
    word = await DictionaryService.get_word_by_id(word_id)
    if not word:
        return jsonify({"error": "Word not found"}), 404

    data = serialize_word_detail(word)
    return jsonify(data)


async def _search_by_keys(
    session, query_str: str, limit: int, results_map: dict[int, dict[str, Any]]
) -> None:
    key_query = (
        select(Definition, Word, Type, Key.word.label("matched_key"))
        .join(Word, Definition.word_id == Word.id)
        .outerjoin(Type, Word.type_id == Type.id)
        .join(Definition.keys)
        .where(func.lower(Key.word).like(f"{query_str.lower()}%"))
        .options(selectinload(Definition.source_word))
        .limit(limit * 3)
    )
    key_res = await session.execute(key_query)
    for row in key_res:
        d, w, t, matched_k = row[0], row[1], row[2], row[3]
        if w.id in results_map:
            results_map[w.id]["match_count"] += 1
            continue

        grammar = (str(d.slots or "") + str(d.grammar_code or "")) or None
        results_map[w.id] = {
            "word_id": w.id,
            "word_name": w.name,
            "type_name": t.type_ if t else None,
            "grammar": grammar,
            "snippet": f"«{matched_k}»: {d.body or ''}",
            "match_count": 1,
        }
        if len(results_map) >= limit:
            break


async def _search_by_body(
    session, query_str: str, limit: int, results_map: dict[int, dict[str, Any]]
) -> None:
    remaining = limit - len(results_map)
    body_query = (
        select(Definition, Word, Type)
        .join(Word, Definition.word_id == Word.id)
        .outerjoin(Type, Word.type_id == Type.id)
        .where(func.lower(Definition.body).like(f"%{query_str.lower()}%"))
        .limit(remaining * 3)
    )
    body_res = await session.execute(body_query)
    pattern = re.compile(re.escape(query_str), re.IGNORECASE)
    for d, w, t in body_res:
        if w.id in results_map:
            results_map[w.id]["match_count"] += 1
            continue

        body_text = d.body or ""
        snippet = pattern.sub(lambda m: f"«{m.group(0)}»", body_text)
        grammar = (str(d.slots or "") + str(d.grammar_code or "")) or None

        results_map[w.id] = {
            "word_id": w.id,
            "word_name": w.name,
            "type_name": t.type_ if t else None,
            "grammar": grammar,
            "snippet": snippet,
            "match_count": 1,
        }
        if len(results_map) >= limit:
            break


# ─── English -> Loglan Search ────────────────────────────────────────────────
@api_bp.route("/search/english", methods=["GET"])
@optional_auth
async def search_english():
    """
    Search definitions by English keyword or body content.
    Query parameters:
      - query: search term
      - use_keywords / use_keywords_only: search by key words (default: true)
      - use_like: search definition body by substring (default: false)
      - limit: max results (default: 50)
    """
    query_str = request.args.get("query", "").strip()
    if not query_str:
        return jsonify([])

    use_kw_param = request.args.get("use_keywords")
    if use_kw_param is None:
        use_kw_param = request.args.get("use_keywords_only", "true")
    use_keywords = str(use_kw_param).lower() in ("true", "1", "yes")

    use_like = request.args.get("use_like", "false").lower() in ("true", "1", "yes")
    limit = min(int(request.args.get("limit", 50)), 300)

    results_map: dict[int, dict[str, Any]] = {}

    async with async_session_maker() as session:
        if use_keywords:
            await _search_by_keys(session, query_str, limit, results_map)
        if use_like and len(results_map) < limit:
            await _search_by_body(session, query_str, limit, results_map)

    return jsonify(list(results_map.values()))


# ─── Types, Events, Authors Lookups ──────────────────────────────────────────
@api_bp.route("/types", methods=["GET"])
async def get_types():
    """Retrieve all word types/groups with word counts."""
    async with async_session_maker() as session:
        query = (
            select(
                Type,
                func.count(Word.id).label("word_count"),
            )
            .outerjoin(Word, Word.type_id == Type.id)
            .group_by(Type.id)
            .order_by(Type.type_)
        )
        res = await session.execute(query)
        items = [serialize_type(t, word_count=cnt) for t, cnt in res]
        return jsonify(items)


@api_bp.route("/events", methods=["GET"])
async def get_events():
    """Retrieve all dictionary editions and events."""
    async with async_session_maker() as session:
        events = await BaseSelector(model=Event).all_async(session)
        return jsonify([serialize_event(e) for e in events])


@api_bp.route("/events/<int:event_id>/words", methods=["GET"])
async def get_event_words(event_id: int):
    """Retrieve words added and removed in a specific event: [added_words, removed_words]."""
    async with async_session_maker() as session:
        ev = await session.get(Event, event_id)
        target_ev = ev.event_id if ev else event_id

        added_res = await session.execute(
            select(Word.name).where(Word.event_start_id == target_ev).order_by(Word.name)
        )
        added = [r[0] for r in added_res]

        removed_res = await session.execute(
            select(Word.name).where(Word.event_end_id == target_ev).order_by(Word.name)
        )
        removed = [r[0] for r in removed_res]

        return jsonify([added, removed])


@api_bp.route("/authors", methods=["GET"])
async def get_authors():
    """Retrieve all authors with word counts."""
    async with async_session_maker() as session:
        query = (
            select(
                Author,
                func.count(Word.id).label("word_count"),
            )
            .outerjoin(Author.contribution)
            .group_by(Author.id)
            .order_by(Author.abbreviation)
        )
        res = await session.execute(query)
        items = [serialize_author(a, word_count=cnt) for a, cnt in res]
        return jsonify(items)


@api_bp.route("/stats", methods=["GET"])
async def get_stats():
    """Retrieve database summary statistics matching DbStats contract."""
    async with async_session_maker() as session:
        w_cnt = (await session.execute(select(func.count(Word.id)))).scalar() or 0
        d_cnt = (await session.execute(select(func.count(Definition.id)))).scalar() or 0
        e_cnt = (await session.execute(select(func.count(Event.id)))).scalar() or 0
        t_cnt = (await session.execute(select(func.count(Type.id)))).scalar() or 0
        a_cnt = (await session.execute(select(func.count(Author.id)))).scalar() or 0

        # Affixes count
        affix_type = (await session.execute(select(Type.id).where(Type.type_x == "Affix"))).scalar()
        aff_cnt = 0
        if affix_type:
            aff_cnt = (
                await session.execute(select(func.count(Word.id)).where(Word.type_id == affix_type))
            ).scalar() or 0

        # Settings
        settings_query = select(Setting).order_by(Setting.id.desc()).limit(1)
        setting_row = (await session.execute(settings_query)).scalar_one_or_none()
        settings_list: list[dict[str, str]] = []
        if setting_row:
            if setting_row.date:
                settings_list.append({"key": "date", "value": str(setting_row.date)})
            if setting_row.db_version is not None:
                settings_list.append({"key": "db_version", "value": str(setting_row.db_version)})
            if setting_row.last_word_id is not None:
                settings_list.append(
                    {"key": "last_word_id", "value": str(setting_row.last_word_id)}
                )
            if setting_row.db_release:
                settings_list.append({"key": "db_release", "value": str(setting_row.db_release)})
        if not settings_list:
            settings_list = [
                {"key": "db_version", "value": "PostgreSQL"},
                {"key": "db_release", "value": "Neon"},
            ]

        return jsonify(
            {
                "db_path": "PostgreSQL (Remote)",
                "word_count": w_cnt,
                "definition_count": d_cnt,
                "event_count": e_cnt,
                "type_count": t_cnt,
                "author_count": a_cnt,
                "affix_count": aff_cnt,
                "spelling_count": w_cnt,
                "settings": settings_list,
                "db_version": "PostgreSQL",
                "db_release": "Neon",
            }
        )


# ─── Admin Mutations ──────────────────────────────────────────────────────────
@api_bp.route("/words", methods=["POST"])
@require_admin
async def create_word():
    """Create a new word entry (admin only)."""
    payload = await request.get_json()
    if not payload or not payload.get("name"):
        return jsonify({"error": "Word name is required"}), 400

    name = payload["name"].strip()
    async with async_session_maker() as session:
        # Resolve type_id
        type_id = payload.get("type_id")
        if not type_id and payload.get("type_name"):
            t = (
                await session.execute(select(Type).where(Type.type_ == payload["type_name"]))
            ).scalar_one_or_none()
            if t:
                type_id = t.id

        # Resolve event_start_id and event_end_id
        event_start_id = payload.get("event_start_id")
        if not event_start_id and payload.get("event_start"):
            ev = (
                await session.execute(select(Event).where(Event.name == payload["event_start"]))
            ).scalar_one_or_none()
            if ev:
                event_start_id = ev.event_id

        event_end_id = payload.get("event_end_id")
        if not event_end_id and payload.get("event_end"):
            ev = (
                await session.execute(select(Event).where(Event.name == payload["event_end"]))
            ).scalar_one_or_none()
            if ev:
                event_end_id = ev.event_id

        year_date = parse_year(payload.get("year"))

        word = Word(
            name=name,
            type_id=type_id,
            event_start_id=event_start_id or 1,
            event_end_id=event_end_id,
            year=year_date,
            rank=str(payload["rank"]) if payload.get("rank") is not None else None,
            match=payload.get("match_") or payload.get("match"),
            origin=payload.get("origin"),
            origin_x=payload.get("origin_x"),
            notes=payload.get("notes"),
        )
        session.add(word)
        await session.commit()
        await session.refresh(word)
        DictionaryService.clear_cache()

        loaded_word = await DictionaryService.get_word_by_id(word.id)
        return jsonify(serialize_word_detail(loaded_word or word)), 201


async def _resolve_word_type_id(session, payload: dict[str, Any]) -> int | None:
    if "type_id" in payload:
        return payload["type_id"]
    if "type_name" in payload:
        if not payload["type_name"]:
            return None
        t = (
            await session.execute(select(Type).where(Type.type_ == payload["type_name"]))
        ).scalar_one_or_none()
        return t.id if t else None
    return None


async def _resolve_word_events(
    session, payload: dict[str, Any]
) -> tuple[int | None, int | None, bool, bool]:
    s_chg = "event_start" in payload or "event_start_id" in payload
    e_chg = "event_end" in payload or "event_end_id" in payload
    ev_start, ev_end = None, None

    if "event_start" in payload:
        name = payload["event_start"]
        if name:
            ev = (
                await session.execute(select(Event).where(Event.name == name))
            ).scalar_one_or_none()
            ev_start = ev.event_id if ev else 1
        else:
            ev_start = 1
    elif "event_start_id" in payload:
        ev_start = payload["event_start_id"]

    if "event_end" in payload:
        name = payload["event_end"]
        if name:
            ev = (
                await session.execute(select(Event).where(Event.name == name))
            ).scalar_one_or_none()
            ev_end = ev.event_id if ev else None
    elif "event_end_id" in payload:
        ev_end = payload["event_end_id"]

    return ev_start, ev_end, s_chg, e_chg


def _apply_word_scalar_fields(word: Word, payload: dict[str, Any]) -> None:
    if "year" in payload:
        word.year = parse_year(payload.get("year"))
    if "rank" in payload:
        word.rank = str(payload["rank"]) if payload["rank"] is not None else None
    if "match_" in payload:
        word.match = payload["match_"]
    elif "match" in payload:
        word.match = payload["match"]
    if "origin" in payload:
        word.origin = payload["origin"]
    if "origin_x" in payload:
        word.origin_x = payload["origin_x"]
    if "notes" in payload:
        word.notes = payload["notes"]


async def _update_word_model(session, word: Word, payload: dict[str, Any]) -> None:
    if payload.get("name"):
        word.name = payload["name"].strip()

    if "type_id" in payload or "type_name" in payload:
        word.type_id = await _resolve_word_type_id(session, payload)

    ev_start, ev_end, s_chg, e_chg = await _resolve_word_events(session, payload)
    if s_chg:
        word.event_start_id = ev_start
    if e_chg:
        word.event_end_id = ev_end

    _apply_word_scalar_fields(word, payload)


@api_bp.route("/words/<int:word_id>", methods=["PUT"])
@require_admin
async def update_word(word_id: int):
    """Update an existing word entry (admin only)."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        word = await session.get(Word, word_id)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        await _update_word_model(session, word, payload)
        await session.commit()
        DictionaryService.clear_cache()

        loaded_word = await DictionaryService.get_word_by_id(word_id)
        return jsonify(serialize_word_detail(loaded_word or word))


@api_bp.route("/words/<int:word_id>", methods=["DELETE"])
@require_admin
async def delete_word(word_id: int):
    """Delete a word entry (admin only)."""
    async with async_session_maker() as session:
        word = await session.get(Word, word_id)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        word.authors = []
        await session.delete(word)
        await session.commit()
        DictionaryService.clear_cache()
        return jsonify({"ok": True})


# ─── Definition Mutations ─────────────────────────────────────────────────────
@api_bp.route("/words/<int:word_id>/definitions", methods=["POST"])
@require_admin
async def create_definition(word_id: int):
    """Create a definition for a word (admin only)."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        word = await session.get(Word, word_id)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        slots, grammar_code = split_grammar(payload.get("grammar"))
        max_pos = (
            await session.execute(
                select(func.coalesce(func.max(Definition.position), 0)).where(
                    Definition.word_id == word_id
                )
            )
        ).scalar() or 0

        definition = Definition(
            word_id=word_id,
            position=max_pos + 1,
            slots=slots,
            grammar_code=grammar_code,
            usage=payload.get("usage"),
            body=payload.get("body", "").strip(),
            case_tags=payload.get("tags"),
        )
        session.add(definition)
        await session.commit()
        DictionaryService.clear_cache()

        loaded_word = await DictionaryService.get_word_by_id(word_id)
        return jsonify(serialize_word_detail(loaded_word or word)), 201


@api_bp.route("/words/<int:word_id>/definitions/<int:def_id>", methods=["PUT"])
@require_admin
async def update_definition(word_id: int, def_id: int):
    """Update a definition for a word (admin only)."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        definition = await session.get(Definition, def_id)
        if not definition or definition.word_id != word_id:
            return jsonify({"error": "Definition not found"}), 404

        if "grammar" in payload:
            slots, grammar_code = split_grammar(payload.get("grammar"))
            definition.slots = slots
            definition.grammar_code = grammar_code

        if "usage" in payload:
            definition.usage = payload.get("usage")
        if "body" in payload:
            definition.body = payload.get("body", "").strip()
        if "tags" in payload:
            definition.case_tags = payload.get("tags")
        if "position" in payload and payload["position"] is not None:
            definition.position = int(payload["position"])

        await session.commit()
        DictionaryService.clear_cache()

        loaded_word = await DictionaryService.get_word_by_id(word_id)
        word = await session.get(Word, word_id)
        return jsonify(serialize_word_detail(loaded_word or word))


@api_bp.route("/words/<int:word_id>/definitions/<int:def_id>", methods=["DELETE"])
@require_admin
async def delete_definition(word_id: int, def_id: int):
    """Delete a definition from a word (admin only)."""
    async with async_session_maker() as session:
        definition = await session.get(Definition, def_id)
        if not definition or definition.word_id != word_id:
            return jsonify({"error": "Definition not found"}), 404

        await session.delete(definition)
        await session.commit()
        DictionaryService.clear_cache()

        loaded_word = await DictionaryService.get_word_by_id(word_id)
        word = await session.get(Word, word_id)
        return jsonify(serialize_word_detail(loaded_word or word))


# ─── Event Mutations ──────────────────────────────────────────────────────────
@api_bp.route("/events", methods=["POST"])
@require_admin
async def create_event():
    """Create a new event (admin only)."""
    payload = await request.get_json()
    if not payload or not payload.get("name"):
        return jsonify({"error": "Event name is required"}), 400

    async with async_session_maker() as session:
        max_ev_id = (
            await session.execute(select(func.coalesce(func.max(Event.event_id), 0)))
        ).scalar() or 0

        date_val = None
        if payload.get("date"):
            try:
                date_val = datetime.date.fromisoformat(str(payload["date"])[:10])
            except ValueError:
                pass

        event = Event(
            event_id=max_ev_id + 1,
            name=payload["name"].strip(),
            date=date_val,
            definition=payload.get("notes") or payload.get("definition"),
            annotation=payload.get("annotation"),
            suffix=payload.get("suffix"),
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return jsonify(serialize_event(event)), 201


def _update_event_model(event: Event, payload: dict[str, Any]) -> None:
    if payload.get("name"):
        event.name = payload["name"].strip()
    if "date" in payload:
        if payload["date"]:
            try:
                event.date = datetime.date.fromisoformat(str(payload["date"])[:10])
            except ValueError:
                event.date = None
        else:
            event.date = None
    if "notes" in payload:
        event.definition = payload["notes"]
    elif "definition" in payload:
        event.definition = payload["definition"]
    if "annotation" in payload:
        event.annotation = payload["annotation"]
    if "suffix" in payload:
        event.suffix = payload["suffix"]


@api_bp.route("/events/<int:event_id>", methods=["PUT"])
@require_admin
async def update_event(event_id: int):
    """Update an event (admin only)."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        event = await session.get(Event, event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        _update_event_model(event, payload)
        await session.commit()
        await session.refresh(event)
        return jsonify(serialize_event(event))


@api_bp.route("/events/<int:event_id>", methods=["DELETE"])
@require_admin
async def delete_event(event_id: int):
    """Delete an event (admin only)."""
    async with async_session_maker() as session:
        event = await session.get(Event, event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        in_use = (
            await session.execute(
                select(func.count(Word.id)).where(
                    (Word.event_start_id == event.event_id) | (Word.event_end_id == event.event_id)
                )
            )
        ).scalar() or 0

        if in_use > 0:
            return jsonify({"error": f"Cannot delete event: used by {in_use} word(s)"}), 400

        await session.delete(event)
        await session.commit()
        return jsonify({"ok": True})


# ─── Type Mutations ───────────────────────────────────────────────────────────
@api_bp.route("/types", methods=["POST"])
@require_admin
async def create_type():
    """Create a new word type (admin only). Returns updated list of types."""
    payload = await request.get_json()
    if not payload or not payload.get("name"):
        return jsonify({"error": "Type name is required"}), 400

    async with async_session_maker() as session:
        t = Type(
            type_=payload["name"].strip(),
            type_x=payload.get("type_x"),
            group=payload.get("group_") or payload.get("group"),
            parentable=payload.get("parentable", True),
            description=payload.get("description"),
        )
        session.add(t)
        await session.commit()

    return await get_types()


@api_bp.route("/types/<int:type_id>", methods=["PUT"])
@require_admin
async def update_type(type_id: int):
    """Update a word type (admin only). Returns updated list of types."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        t = await session.get(Type, type_id)
        if not t:
            return jsonify({"error": "Type not found"}), 404

        if "name" in payload and payload["name"]:
            t.type_ = payload["name"].strip()
        if "type_x" in payload:
            t.type_x = payload["type_x"]
        if "group_" in payload:
            t.group = payload["group_"]
        elif "group" in payload:
            t.group = payload["group"]
        if "parentable" in payload:
            t.parentable = payload["parentable"]
        if "description" in payload:
            t.description = payload["description"]

        await session.commit()

    return await get_types()


@api_bp.route("/types/<int:type_id>", methods=["DELETE"])
@require_admin
async def delete_type(type_id: int):
    """Delete a word type (admin only). Returns updated list of types."""
    async with async_session_maker() as session:
        t = await session.get(Type, type_id)
        if not t:
            return jsonify({"error": "Type not found"}), 404

        in_use = (
            await session.execute(select(func.count(Word.id)).where(Word.type_id == type_id))
        ).scalar() or 0

        if in_use > 0:
            return jsonify({"error": f"Cannot delete type: used by {in_use} word(s)"}), 400

        await session.delete(t)
        await session.commit()

    return await get_types()


# ─── Author Mutations ─────────────────────────────────────────────────────────
@api_bp.route("/authors", methods=["POST"])
@require_admin
async def create_author():
    """Create a new author (admin only). Returns updated list of authors."""
    payload = await request.get_json()
    abbr = payload.get("initials") or payload.get("abbreviation") if payload else None
    if not payload or not abbr:
        return jsonify({"error": "Author initials/abbreviation is required"}), 400

    async with async_session_maker() as session:
        author = Author(
            abbreviation=abbr.strip(),
            full_name=payload.get("full_name"),
            notes=payload.get("notes"),
        )
        session.add(author)
        await session.commit()

    return await get_authors()


@api_bp.route("/authors/<int:author_id>", methods=["PUT"])
@require_admin
async def update_author(author_id: int):
    """Update an author (admin only). Returns updated list of authors."""
    payload = await request.get_json()
    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    async with async_session_maker() as session:
        author = await session.get(Author, author_id)
        if not author:
            return jsonify({"error": "Author not found"}), 404

        abbr = payload.get("initials") or payload.get("abbreviation")
        if abbr:
            author.abbreviation = abbr.strip()
        if "full_name" in payload:
            author.full_name = payload["full_name"]
        if "notes" in payload:
            author.notes = payload["notes"]

        await session.commit()

    return await get_authors()


@api_bp.route("/authors/<int:author_id>", methods=["DELETE"])
@require_admin
async def delete_author(author_id: int):
    """Delete an author (admin only). Returns updated list of authors."""
    async with async_session_maker() as session:
        author = await session.get(Author, author_id)
        if not author:
            return jsonify({"error": "Author not found"}), 404

        await session.delete(author)
        await session.commit()

    return await get_authors()
