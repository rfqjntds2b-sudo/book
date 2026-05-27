from datetime import datetime, timezone

from book_blog_bot.crawler import Book
from book_blog_bot.scheduler import select_unposted_books


def test_select_unposted_books_skips_state_entries_and_limits_count():
    books = [
        Book("Book A", "£1.00", "One", "In stock", "https://example.com/a"),
        Book("Book B", "£2.00", "Two", "In stock", "https://example.com/b"),
        Book("Book C", "£3.00", "Three", "In stock", "https://example.com/c"),
    ]
    posted = {"https://example.com/a": datetime(2026, 5, 27, tzinfo=timezone.utc).isoformat()}

    selected = select_unposted_books(books, posted, count=2)

    assert [book.title for book in selected] == ["Book B", "Book C"]
