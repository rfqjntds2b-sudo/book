from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime

from .crawler import Book


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().replace("'", "")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "book"


def render_hugo_post(book: Book, posted_at: datetime) -> str:
    title = json.dumps(book.title, ensure_ascii=False)
    source_url = json.dumps(book.source_url, ensure_ascii=False)
    price = json.dumps(book.price, ensure_ascii=False)
    rating = json.dumps(book.rating, ensure_ascii=False)
    availability = json.dumps(book.availability, ensure_ascii=False)

    return f"""---
title: {title}
date: {posted_at.isoformat()}
draft: false
tags: ["books", "books-to-scrape"]
categories: ["book-crawling"]
source_url: {source_url}
price: {price}
rating: {rating}
availability: {availability}
---

## {book.title}

- 가격: {book.price}
- 평점: {book.rating}
- 재고: {book.availability}

[원문 보기]({book.source_url})
"""
