# Books to Scrape Hugo Bot

`https://books.toscrape.com/`의 카탈로그 5페이지를 크롤링하고, 책 5권을 Hugo Markdown 글로 변환한 뒤, 5분에 1개씩 GitHub 블로그 저장소에 커밋/푸시하는 봇입니다.

## 프로세스

1. `Books to Scrape` 카탈로그 5페이지를 순서대로 수집합니다.
2. 아직 게시하지 않은 책 5권을 고릅니다.
3. 각 책을 `content/posts/*.md` Hugo 글로 변환합니다.
4. 글 1개를 만들 때마다 `scripts/git_push.sh`가 `git add`, `git commit`, `git push`를 실행합니다.
5. 다음 글 게시 전 300초, 즉 5분을 기다립니다.

## GitHub 연결

이 폴더가 아직 Git 저장소가 아니라면 처음 한 번만 설정합니다.

```bash
git init
git branch -M main
git remote add origin git@github.com:<USER>/<REPO>.git
```

`hugo.toml`의 `baseURL`도 본인 GitHub Pages 주소로 바꿔주세요.

## 실행 명령어

```bash
BOOK_BOT_BRANCH=main ./scripts/run_book_bot.sh
```

테스트 실행은 아래처럼 할 수 있습니다.

```bash
python3 -m pytest -q
```

실제 push 없이 크롤링/Markdown 생성만 확인하려면:

```bash
BOOK_BOT_INTERVAL_SECONDS=0 ./scripts/run_book_bot.sh --dry-run
```
