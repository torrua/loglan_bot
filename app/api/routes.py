"""REST API route handlers for LOD Manager Telegram Mini App and Web."""

from __future__ import annotations

import re
from typing import Any

from loglan_core import Author, BaseSelector, Definition, Event, Key, Type, Word
from quart import jsonify, request
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


# ─── Health check ─────────────────────────────────────────────────────────────
@api_bp.route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "app": "Loglan Dictionary API"})


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


# ─── English -> Loglan Search ────────────────────────────────────────────────
@api_bp.route("/search/english", methods=["GET"])
@optional_auth
async def search_english():
    """
    Search definitions by English keyword or body content.
    Query parameters:
      - query: search term
      - use_keywords: search by key words (default: true)
      - use_like: search definition body by substring (default: false)
      - limit: max results (default: 50)
    """
    query_str = request.args.get("query", "").strip()
    if not query_str:
        return jsonify([])

    use_keywords = request.args.get("use_keywords", "true").lower() in ("true", "1", "yes")
    use_like = request.args.get("use_like", "false").lower() in ("true", "1", "yes")
    limit = min(int(request.args.get("limit", 50)), 100)

    results: list[dict[str, Any]] = []
    seen_def_ids: set[int] = set()

    async with async_session_maker() as session:
        # Strategy 1: Search by key words
        if use_keywords:
            key_query = (
                select(Definition, Word, Type, Key.word.label("matched_key"))
                .join(Word, Definition.word_id == Word.id)
                .outerjoin(Type, Word.type_id == Type.id)
                .join(Definition.keys)
                .where(func.lower(Key.word).like(f"{query_str.lower()}%"))
                .options(selectinload(Definition.source_word))
                .limit(limit)
            )
            key_res = await session.execute(key_query)
            for row in key_res:
                d = row[0]
                w = row[1]
                t = row[2]
                matched_k = row[3]
                if d.id in seen_def_ids:
                    continue
                seen_def_ids.add(d.id)

                grammar = (str(d.slots or "") + str(d.grammar_code or "")) or None
                results.append(
                    {
                        "word_id": w.id,
                        "word_name": w.name,
                        "type_name": t.type_ if t else None,
                        "grammar": grammar,
                        "body": d.body or "",
                        "snippet": f"<b>{matched_k}</b>: {d.body}",
                        "matched_key": matched_k,
                    }
                )

        # Strategy 2: Search definition body
        if use_like and len(results) < limit:
            remaining = limit - len(results)
            body_query = (
                select(Definition, Word, Type)
                .join(Word, Definition.word_id == Word.id)
                .outerjoin(Type, Word.type_id == Type.id)
                .where(func.lower(Definition.body).like(f"%{query_str.lower()}%"))
                .limit(remaining)
            )
            body_res = await session.execute(body_query)
            for d, w, t in body_res:
                if d.id in seen_def_ids:
                    continue
                seen_def_ids.add(d.id)

                body_text = d.body or ""
                # Simple highlight
                pattern = re.compile(re.escape(query_str), re.IGNORECASE)
                snippet = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", body_text)
                grammar = (str(d.slots or "") + str(d.grammar_code or "")) or None

                results.append(
                    {
                        "word_id": w.id,
                        "word_name": w.name,
                        "type_name": t.type_ if t else None,
                        "grammar": grammar,
                        "body": body_text,
                        "snippet": snippet,
                        "matched_key": None,
                    }
                )

    return jsonify(results)


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
            select(Word.name)
            .where(Word.event_start_id == target_ev)
            .order_by(Word.name)
        )
        added = [r[0] for r in added_res]

        removed_res = await session.execute(
            select(Word.name)
            .where(Word.event_end_id == target_ev)
            .order_by(Word.name)
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
    """Retrieve database summary statistics."""
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

        return jsonify(
            {
                "word_count": w_cnt,
                "definition_count": d_cnt,
                "event_count": e_cnt,
                "type_count": t_cnt,
                "author_count": a_cnt,
                "affix_count": aff_cnt,
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

    async with async_session_maker() as session:
        word = Word(
            name=payload["name"].strip(),
            type_id=payload.get("type_id"),
            rank=payload.get("rank"),
            match=payload.get("match_"),
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

        if "name" in payload:
            word.name = payload["name"].strip()
        if "type_id" in payload:
            word.type_id = payload["type_id"]
        if "rank" in payload:
            word.rank = payload["rank"]
        if "match_" in payload:
            word.match = payload["match_"]
        if "origin" in payload:
            word.origin = payload["origin"]
        if "origin_x" in payload:
            word.origin_x = payload["origin_x"]
        if "notes" in payload:
            word.notes = payload["notes"]

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

        await session.delete(word)
        await session.commit()
        DictionaryService.clear_cache()
        return jsonify({"ok": True})
