from pathlib import Path

import pytest

from book_blog_bot.scheduler import PublishEnvironmentError, ensure_publish_environment


def test_ensure_publish_environment_rejects_non_git_site_before_generating_posts(tmp_path):
    push_script = tmp_path / "scripts" / "git_push.sh"
    push_script.parent.mkdir()
    push_script.write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    with pytest.raises(PublishEnvironmentError, match="git 저장소가 아닙니다"):
        ensure_publish_environment(
            site_root=tmp_path,
            push_script=push_script,
            dry_run=False,
        )


def test_ensure_publish_environment_allows_dry_run_without_git(tmp_path):
    push_script = tmp_path / "missing.sh"

    ensure_publish_environment(
        site_root=tmp_path,
        push_script=push_script,
        dry_run=True,
    )
