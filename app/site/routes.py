import os

from quart import Blueprint, redirect, url_for, render_template, request, jsonify
from loglan_core import WordSelector, Event, BaseSelector, DefinitionSelector

from app.engine import async_session_maker
from app.site.compose.english_item import EnglishItem
from app.site.compose.loglan_item import Composer
from app.site.functions import get_data

site_blueprint = Blueprint(
    "site",
    __name__,
    template_folder="site/templates",
)
DEFAULT_SEARCH_LANGUAGE = os.getenv("DEFAULT_SEARCH_LANGUAGE", "log")
DEFAULT_HTML_STYLE = os.getenv("DEFAULT_HTML_STYLE", "normal")
MAIN_SITE = "http://www.loglan.org/"


@site_blueprint.route("/Articles/")
def redirect_articles():
    return redirect(url_for("articles"))


@site_blueprint.route("/Texts/")
def redirect_texts():
    return redirect(url_for("texts"))


@site_blueprint.route("/Sanpa/")
@site_blueprint.route("/Lodtua/")
def redirect_columns():
    return redirect(url_for("columns"))


@site_blueprint.route("/")
@site_blueprint.route("/home")
async def home():
    article = get_data(MAIN_SITE).body.find("div", {"id": "content"})
    for bq in article.findAll("blockquote"):
        bq["class"] = "blockquote"

    for img in article.findAll("img"):
        img["src"] = MAIN_SITE + img["src"]

    return await render_template(
        "home.html",
        article="",
    )


@site_blueprint.route("/articles")
async def articles():
    article_block = get_data(MAIN_SITE)
    title = article_block.find("a", {"name": "articles"}).find_parent("h2")
    content = title.find_next("ol")
    return await render_template(
        "articles.html",
        articles=content,
        title=title.get_text(),
    )


@site_blueprint.route("/texts")
async def texts():
    article_block = get_data(MAIN_SITE)
    title = article_block.find("a", {"name": "texts"}).find_parent("h2")
    content = title.find_next("ol")
    return await render_template(
        "articles.html",
        articles=content,
        title=title.get_text(),
    )


@site_blueprint.route("/columns")
async def columns():
    article_block = get_data(MAIN_SITE)
    title = article_block.find("a", {"name": "columns"}).find_parent("h2")
    content = title.find_next("ul")
    return await render_template(
        "articles.html",
        articles=content,
        title=title.get_text(),
    )


@site_blueprint.route("/dictionary")
@site_blueprint.route("/dictionary/")
async def dictionary():
    async with async_session_maker() as session:
        events = await BaseSelector(model=Event).all_async(session)
    events = {int(event.id): event.name for event in reversed(events)}
    content = await generate_content(request.args)
    return await render_template(
        "dictionary.html",
        content=content,
        events=events,
    )


@site_blueprint.route("/how_to_read")
async def how_to_read():
    return await render_template("reading.html")


@site_blueprint.route("/submit_search", methods=["POST"])
async def submit_search():

    res = await request.form
    return await generate_content(res)


def strtobool(val):
    val = val.lower()
    if val in ("yes", "true", "t", "y", "1"):
        return True
    if val in ("no", "false", "f", "n", "0"):
        return False
    raise ValueError("Invalid boolean value")


async def generate_content(data):
    word = data.get("word", str())
    search_language = data.get("language_id", DEFAULT_SEARCH_LANGUAGE)
    event_id = int(data.get("event_id", 1))
    is_case_sensitive = data.get("case_sensitive", False)

    if not word or not data:
        return jsonify(result="<div></div>")

    nothing = """
<div class="alert alert-secondary" role="alert" style="text-align: center;">
  %s
</div>
    """

    if isinstance(is_case_sensitive, str):
        is_case_sensitive = strtobool(is_case_sensitive)

    result = await search_all(
        search_language, word, event_id, is_case_sensitive, nothing
    )
    return jsonify(result=result)


async def search_all(search_language, word, event_id, is_case_sensitive, nothing):
    if search_language == "log":
        result = await search_log(word, event_id, is_case_sensitive, nothing)

    elif search_language == "eng":
        result = await search_eng(word, event_id, is_case_sensitive, nothing)
    else:
        result = nothing % f"Sorry, but nothing was found for <b>{word}</b>."
    return result


async def search_eng(word, event_id, is_case_sensitive, nothing):

    async with async_session_maker() as session:
        definitions = await (
            DefinitionSelector(case_sensitive=is_case_sensitive)
            .with_relationships("source_word")
            .by_key(key=word)
            .by_event(event_id=int(event_id))
            .all_async(session, unique=True)
        )
        result = EnglishItem(
            definitions=definitions, key=word, style=DEFAULT_HTML_STYLE
        ).export_as_html()

    if not result:
        result = (
            nothing
            % f"There is no word <b>{word}</b> in English. Try switching to Loglan"
            f"{' or disable Case sensitive search' if is_case_sensitive else ''}."
        )
    return result


async def search_log(word: str, event_id: int, is_case_sensitive: bool, nothing):

    async with async_session_maker() as session:
        word_result = await (
            WordSelector(case_sensitive=bool(is_case_sensitive))
            .with_relationships()
            .by_name(name=str(word))
            .by_event(event_id=int(event_id))
            .all_async(session, unique=True)
        )
        result = Composer(words=word_result, style=DEFAULT_HTML_STYLE).export_as_html()
    if not result:
        result = (
            nothing
            % f"There is no word <b>{word}</b> in Loglan. Try switching to English"
            f"{' or disable Case sensitive search' if is_case_sensitive else ''}."
        )
    return result


@site_blueprint.route("/<string:section>/", methods=["GET"])
@site_blueprint.route("/<string:section>/<string:article>", methods=["GET"])
async def proxy(section: str = "", article: str = ""):
    url = f"{MAIN_SITE}{section}/{article}"
    content = get_data(url).body

    for bq in content.findAll("blockquote"):
        bq["class"] = "blockquote"

    for img in content.findAll("img"):
        img["src"] = MAIN_SITE + section + "/" + img["src"]

    name_of_article = content.h1.extract().get_text()
    return await render_template(
        "article.html",
        name_of_article=name_of_article,
        article=content,
        title=section,
    )
