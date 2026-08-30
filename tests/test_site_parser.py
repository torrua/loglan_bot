"""Unit tests for LoglanContentParser and content sanitizer"""

from bs4 import BeautifulSoup

from app.site.parser import LoglanContentParser

SAMPLE_INDEX_HTML = """
<html>
<body>
    <h2><a name="articles">Articles</a></h2>
    <ol>
        <li>
            <a href="Articles/faces-of-gu.html">The Many Faces of <b>Gu</b></a><br>
            An explanation of gu and its kin, by Robert McIvor.
        </li>
        <li>
            <a href="Articles/simple-article.html">Simple Article</a><br>
            A general overview of language principles.
        </li>
    </ol>

    <h2><a name="texts">Sample Texts</a></h2>
    <ol>
        <li>
            <a href="Texts/vizka-la-spat.html">Vizka La Spat</a><br>
            A cartoon story in Loglan by Rex May.
        </li>
    </ol>
</body>
</html>
"""

SAMPLE_ARTICLE_HTML = """
<html>
<head><title>Original Article Title</title></head>
<body bgcolor="#FFFFFF" text="#000000">
    <p>(A page from the <a href="http://www.loglan.org">Loglan web site</a>.)</p>
    <script>alert("malicious");</script>
    <h1>The Many Faces of Gu</h1>
    <p>By Robert McIvor</p>
    <p>Here is an explanation of <b>gu</b>. See also <a href="other-article.html">Other Article</a> and <a href="http://external.com">External Site</a>.</p>
    <p>Refer to <a href="http://www.loglan.org/Texts/sample.html">Sample Text</a>.</p>
    <img src="diagram.gif" alt="Diagram">
    <table border="1"><tr><td>Cell</td></tr></table>
    <blockquote>Some quote</blockquote>
</body>
</html>
"""


def test_parse_section_articles():
    soup = BeautifulSoup(SAMPLE_INDEX_HTML, "lxml")
    articles = LoglanContentParser.parse_section(soup, "articles")

    assert len(articles) == 2
    assert articles[0].title == "The Many Faces of Gu"
    assert articles[0].url == "/site/Articles/faces-of-gu.html"
    assert articles[0].author == "Robert McIvor"
    assert "An explanation of gu" in articles[0].description
    assert articles[0].section == "articles"

    assert articles[1].title == "Simple Article"
    assert articles[1].author is None
    assert "general overview" in articles[1].description


def test_parse_section_texts():
    soup = BeautifulSoup(SAMPLE_INDEX_HTML, "lxml")
    texts = LoglanContentParser.parse_section(soup, "texts")

    assert len(texts) == 1
    assert texts[0].title == "Vizka La Spat"
    assert texts[0].url == "/site/Texts/vizka-la-spat.html"
    assert texts[0].author == "Rex May"


def test_clean_article_html():
    soup = BeautifulSoup(SAMPLE_ARTICLE_HTML, "lxml")
    title, clean_html = LoglanContentParser.clean_article_html(
        soup, section="Articles", current_article="faces-of-gu.html"
    )

    assert title == "The Many Faces of Gu"
    # Boilerplate removed
    assert "A page from the" not in clean_html
    # Script removed
    assert "<script" not in clean_html
    assert "alert(" not in clean_html
    # Relative link rewritten with section
    assert 'href="/site/Articles/other-article.html"' in clean_html
    # External link has target="_blank"
    assert 'href="http://external.com"' in clean_html
    assert 'target="_blank"' in clean_html
    # Loglan.org absolute link rewritten to local /site/
    assert 'href="/site/Texts/sample.html"' in clean_html
    # Image src normalized to absolute URL
    assert 'src="http://www.loglan.org/Articles/diagram.gif"' in clean_html
    assert 'class="img-fluid my-2 rounded shadow-sm"' in clean_html
    # Bootstrap classes added
    assert "table table-hover table-bordered" in clean_html
    assert "blockquote p-3 my-3" in clean_html
    # Obsolete attributes removed
    assert "bgcolor=" not in clean_html


def test_resolve_relative_link():
    assert (
        LoglanContentParser._resolve_relative_link("/Articles/test.html", "Articles")
        == "/site/Articles/test.html"
    )
    assert (
        LoglanContentParser._resolve_relative_link("../Texts/sample.html", "Articles")
        == "/site/Texts/sample.html"
    )
    assert (
        LoglanContentParser._resolve_relative_link("next-chapter.html", "Loglan1")
        == "/site/Loglan1/next-chapter.html"
    )
