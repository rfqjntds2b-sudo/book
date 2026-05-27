from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .crawler import Book
from .markdown import render_hugo_post, slugify


class PublishEnvironmentError(RuntimeError):
    pass


def ensure_publish_environment(site_root: Path, push_script: Path, dry_run: bool = False) -> None:
    if dry_run:
        return

    if not push_script.exists():
        raise PublishEnvironmentError(f"git push 스크립트가 없습니다: {push_script}")

    git_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=site_root,
        capture_output=True,
        text=True,
    )
    if git_root.returncode != 0:
        raise PublishEnvironmentError(
            "현재 폴더가 git 저장소가 아닙니다. 먼저 `git init` 후 GitHub remote를 연결하세요."
        )

    origin = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=site_root,
        capture_output=True,
        text=True,
    )
    if origin.returncode != 0:
        raise PublishEnvironmentError(
            "origin remote가 없습니다. 예: `git remote add origin git@github.com:<USER>/<REPO>.git`"
        )


def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def select_unposted_books(books: list[Book], posted: dict[str, str], count: int) -> list[Book]:
    return [book for book in books if book.source_url not in posted][:count]


def write_hugo_post(book: Book, content_dir: Path, posted_at: datetime) -> Path:
    content_dir.mkdir(parents=True, exist_ok=True)
    filename = f"books-to-scrape-{slugify(book.title)}.md"
    post_path = content_dir / filename
    post_path.write_text(render_hugo_post(book, posted_at=posted_at), encoding="utf-8")
    return post_path


def push_post(push_script: Path, post_path: Path, dry_run: bool = False) -> None:
    if dry_run:
        return
    subprocess.run([str(push_script), str(post_path)], check=True)


def publish_books_with_interval(
    books: list[Book],
    site_root: Path,
    content_dir: Path,
    push_script: Path,
    state_path: Path,
    count: int = 5,
    interval_seconds: int = 300,
    dry_run: bool = False,
) -> list[Path]:
    ensure_publish_environment(site_root=site_root, push_script=push_script, dry_run=dry_run)

    state = load_state(state_path)
    selected_books = select_unposted_books(books, state, count=count)
    written: list[Path] = []

    for index, book in enumerate(selected_books):
        posted_at = datetime.now(timezone.utc)
        post_path = write_hugo_post(book, content_dir=content_dir, posted_at=posted_at)
        print(f"[{index + 1}/{len(selected_books)}] Hugo 글 생성: {post_path}", flush=True)
        push_post(push_script=push_script, post_path=post_path, dry_run=dry_run)
        if dry_run:
            print(f"[{index + 1}/{len(selected_books)}] dry-run: git push 생략: {book.title}", flush=True)
        else:
            print(f"[{index + 1}/{len(selected_books)}] git push 완료: {book.title}", flush=True)
        state[book.source_url] = posted_at.isoformat()
        save_state(state_path, state)
        written.append(post_path)

        if index < len(selected_books) - 1:
            print(f"다음 게시까지 {interval_seconds}초 대기합니다.", flush=True)
            time.sleep(interval_seconds)

    return written
