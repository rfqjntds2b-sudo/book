from datetime import datetime, timezone

from book_blog_bot.crawler import Book
from book_blog_bot.markdown import render_hugo_post, slugify


def test_slugify_creates_hugo_safe_slug():
    assert slugify("Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)") == "scott-pilgrims-precious-little-life-scott-pilgrim-1"


def test_render_hugo_post_contains_front_matter_and_book_summary():
    book = Book(
        title="A Light in the Attic",
        price="£51.77",
        rating="Three",
        availability="In stock",
        source_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    )

    markdown = render_hugo_post(
        book,
        posted_at=datetime(2026, 5, 27, 6, 20, 0, tzinfo=timezone.utc),
    )

    assert 'title: "A Light in the Attic"' in markdown
    assert "date: 2026-05-27T06:20:00+00:00" in markdown
    assert 'tags: ["books", "books-to-scrape"]' in markdown
    assert "가격: £51.77" in markdown
    assert "평점: Three" in markdown
    assert "[원문 보기](https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html)" in markdown
