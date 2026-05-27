from pathlib import Path

from book_blog_bot.crawler import parse_catalogue_page


def test_parse_catalogue_page_extracts_books_with_absolute_source_urls():
    html = Path("tests/fixtures/catalogue_page.html").read_text(encoding="utf-8")

    books = parse_catalogue_page(
        html,
        page_url="https://books.toscrape.com/catalogue/page-1.html",
    )

    assert [book.title for book in books] == ["A Light in the Attic", "Tipping the Velvet"]
    assert books[0].price == "£51.77"
    assert books[0].rating == "Three"
    assert books[0].availability == "In stock"
    assert books[0].source_url == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    assert books[1].source_url == "https://books.toscrape.com/tipping-the-velvet_999/index.html"
