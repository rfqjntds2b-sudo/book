from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://books.toscrape.com"


@dataclass(frozen=True)
class Book:
    title: str
    price: str
    rating: str
    availability: str
    source_url: str


def _class_names(attrs: list[tuple[str, str | None]]) -> set[str]:
    for name, value in attrs:
        if name == "class" and value:
            return set(value.split())
    return set()


def _attr(attrs: list[tuple[str, str | None]], key: str) -> str | None:
    for name, value in attrs:
        if name == key:
            return value
    return None


class _CatalogueParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.books: list[Book] = []
        self._in_article = False
        self._current: dict[str, str] = {}
        self._capture: str | None = None
        self._capture_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = _class_names(attrs)

        if tag == "article" and "product_pod" in classes:
            self._in_article = True
            self._current = {}
            return

        if not self._in_article:
            return

        if tag == "p" and "star-rating" in classes:
            self._current["rating"] = next(
                (name for name in classes if name not in {"star-rating"}),
                "",
            )
        elif tag == "a" and _attr(attrs, "title") and _attr(attrs, "href"):
            self._current["title"] = _attr(attrs, "title") or ""
            self._current["source_url"] = urljoin(self.page_url, _attr(attrs, "href") or "")
        elif tag == "p" and "price_color" in classes:
            self._start_capture("price")
        elif tag == "p" and "availability" in classes:
            self._start_capture("availability")

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._capture_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture and tag == "p":
            self._current[self._capture] = " ".join("".join(self._capture_parts).split())
            self._capture = None
            self._capture_parts = []

        if tag == "article" and self._in_article:
            self._in_article = False
            if {"title", "price", "rating", "availability", "source_url"} <= self._current.keys():
                self.books.append(
                    Book(
                        title=self._current["title"],
                        price=self._current["price"],
                        rating=self._current["rating"],
                        availability=self._current["availability"],
                        source_url=self._current["source_url"],
                    )
                )
            self._current = {}

    def _start_capture(self, field: str) -> None:
        self._capture = field
        self._capture_parts = []


def parse_catalogue_page(html: str, page_url: str) -> list[Book]:
    parser = _CatalogueParser(page_url)
    parser.feed(html)
    return parser.books


def catalogue_page_url(page_number: int, base_url: str = BASE_URL) -> str:
    if page_number < 1:
        raise ValueError("page_number must be >= 1")
    return f"{base_url.rstrip('/')}/catalogue/page-{page_number}.html"


def fetch_html(url: str, timeout: int = 20) -> str:
    request = Request(
        url,
        headers={"User-Agent": "yeardream-book-blog-bot/0.1 (+https://books.toscrape.com/)"},
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def crawl_books(page_count: int = 5, base_url: str = BASE_URL) -> list[Book]:
    books: list[Book] = []
    for page_number in range(1, page_count + 1):
        page_url = catalogue_page_url(page_number, base_url=base_url)
        books.extend(parse_catalogue_page(fetch_html(page_url), page_url=page_url))
    return books
