from __future__ import annotations

import argparse
from pathlib import Path

from .crawler import BASE_URL, crawl_books
from .scheduler import PublishEnvironmentError, ensure_publish_environment, publish_books_with_interval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl Books to Scrape and publish Hugo posts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="crawl, convert to Markdown, and push posts on a schedule")
    run.add_argument("--pages", type=int, default=5, help="catalogue pages to crawl")
    run.add_argument("--count", type=int, default=5, help="number of posts to publish")
    run.add_argument("--interval-seconds", type=int, default=300, help="delay between each post")
    run.add_argument("--base-url", default=BASE_URL, help="Books to Scrape base URL")
    run.add_argument("--site-root", type=Path, default=Path.cwd(), help="Hugo site root")
    run.add_argument("--content-dir", type=Path, default=None, help="Hugo post directory")
    run.add_argument("--state-file", type=Path, default=None, help="posted-book state file")
    run.add_argument("--push-script", type=Path, default=None, help="script used for git commit and push")
    run.add_argument("--dry-run", action="store_true", help="write posts without running git push")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "run":
        site_root = args.site_root.resolve()
        content_dir = args.content_dir or site_root / "content" / "posts"
        state_file = args.state_file or site_root / ".book_bot_state.json"
        push_script = args.push_script or site_root / "scripts" / "git_push.sh"

        try:
            ensure_publish_environment(site_root=site_root, push_script=push_script, dry_run=args.dry_run)
            books = crawl_books(page_count=args.pages, base_url=args.base_url)
            written = publish_books_with_interval(
                books=books,
                site_root=site_root,
                content_dir=content_dir,
                push_script=push_script,
                state_path=state_file,
                count=args.count,
                interval_seconds=args.interval_seconds,
                dry_run=args.dry_run,
            )
        except PublishEnvironmentError as error:
            raise SystemExit(f"실행 전 설정 필요: {error}") from None

        for path in written:
            print(path)


if __name__ == "__main__":
    main()
