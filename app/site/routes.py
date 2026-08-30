"""Web interface routes for Loglan Online site and dictionary"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from quart import Blueprint, jsonify, redirect, render_template, request, url_for

from app.config import settings
from app.logger import log
from app.services.dictionary import DictionaryService
from app.site.client import MAIN_SITE, site_client
from app.site.compose.english_item import EnglishItem
from app.site.compose.loglan_item import Composer
from app.site.parser import LoglanContentParser

site_blueprint = Blueprint("site", __name__)


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("yes", "true", "t", "y", "1")
    return False


def _to_int(val: Any, default: int = 1) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


@site_blueprint.route("/Articles/")
def redirect_articles():
    return redirect(url_for("site.articles"))


@site_blueprint.route("/Texts/")
def redirect_texts():
    return redirect(url_for("site.texts"))


@site_blueprint.route("/Sanpa/")
@site_blueprint.route("/Lodtua/")
def redirect_columns():
    return redirect(url_for("site.columns"))


@site_blueprint.route("/")
@site_blueprint.route("/home")
async def home():
    """Renders the Home welcome page."""
    return await render_template("home.html")


@site_blueprint.route("/articles")
async def articles():
    """Renders the list of Loglan articles."""
    soup = await site_client.get_soup(MAIN_SITE)
    items = LoglanContentParser.parse_section(soup, "articles") if soup else []

    return await render_template(
        "articles.html",
        items=items,
        title="Articles",
        section_description="In-depth essays, analyses, and linguistic papers on Loglan grammar, vocabulary, and logic.",
    )


@site_blueprint.route("/texts")
async def texts():
    """Renders the list of sample Loglan texts."""
    soup = await site_client.get_soup(MAIN_SITE)
    items = LoglanContentParser.parse_section(soup, "texts") if soup else []

    return await render_template(
        "articles.html",
        items=items,
        title="Sample Texts",
        section_description="Original compositions, translations, and bilingual sample texts to practice reading Loglan.",
    )


@site_blueprint.route("/columns")
async def columns():
    """Renders the list of regular columns from Lognet journal."""
    soup = await site_client.get_soup(MAIN_SITE)
    items = LoglanContentParser.parse_section(soup, "columns") if soup else []

    return await render_template(
        "articles.html",
        items=items,
        title="Regular Columns",
        section_description="Archived columns from the Lognet journal, including Lodtua, Sanpa, and Keugru discussions.",
    )


@site_blueprint.route("/dictionary")
@site_blueprint.route("/dictionary/")
async def dictionary():
    """Renders the interactive dictionary search page."""
    events = await DictionaryService.get_events_map()
    content = await generate_content(request.args)
    return await render_template(
        "dictionary.html",
        content=content,
        events=events,
    )


@site_blueprint.route("/how_to_read")
async def how_to_read():
    """Renders dictionary notations and reading guide."""
    return await render_template("reading.html")


@site_blueprint.route("/submit_search", methods=["POST"])
async def submit_search():
    """AJAX search endpoint."""
    form_data = await request.form
    return await generate_content(form_data)


async def generate_content(data: Mapping[str, Any]):
    """Generates search results HTML based on user input parameters."""
    word = str(data.get("word", "")).strip()
    search_language = str(data.get("language_id", settings.default_search_language)).strip()
    event_id = _to_int(data.get("event_id"), default=1)
    is_case_sensitive = _to_bool(data.get("case_sensitive", False))

    if not word:
        return jsonify(result="<div></div>")

    nothing_tpl = (
        '<div class="alert alert-secondary" role="alert" style="text-align: center;">%s</div>'
    )

    if search_language == "log":
        words = await DictionaryService.get_words_by_name(
            name=word,
            case_sensitive=is_case_sensitive,
            event_id=event_id,
        )
        if words:
            result = Composer(words=words, style=settings.default_html_style).export_as_html()
        else:
            case_hint = " or disable Case sensitive search" if is_case_sensitive else ""
            result = (
                nothing_tpl
                % f"There is no word <b>{word}</b> in Loglan. Try switching to English{case_hint}."
            )

    elif search_language == "eng":
        definitions = await DictionaryService.get_definitions_by_key(
            key=word,
            case_sensitive=is_case_sensitive,
            event_id=event_id,
        )
        if definitions:
            result = EnglishItem(
                definitions=definitions,
                key=word,
                style=settings.default_html_style,
            ).export_as_html()
        else:
            case_hint = " or disable Case sensitive search" if is_case_sensitive else ""
            result = (
                nothing_tpl
                % f"There is no word <b>{word}</b> in English. Try switching to Loglan{case_hint}."
            )
    else:
        result = nothing_tpl % f"Sorry, but nothing was found for <b>{word}</b>."

    return jsonify(result=result)


@site_blueprint.route("/<string:section>/", methods=["GET"])
@site_blueprint.route("/<string:section>/<string:article>", methods=["GET"])
async def proxy(section: str = "", article: str = ""):
    """Proxies, cleans, and styles individual articles from Loglan.org."""
    url = f"{MAIN_SITE}{section}/{article}"
    soup = await site_client.get_soup(url)

    if not soup or not soup.body:
        log.warning("Proxy page not found or failed to load: %s", url)
        return await render_template(
            "article.html",
            name_of_article="Not Found",
            article="<p>Page could not be retrieved from the source site.</p>",
            title=section,
        ), 404

    article_title, clean_html = LoglanContentParser.clean_article_html(
        soup, section=section, current_article=article
    )

    return await render_template(
        "article.html",
        name_of_article=article_title,
        article=clean_html,
        title=section,
    )
