#!/usr/bin/env python3
"""Fetch an archived Reddit submission and render its comment tree."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

API_ROOT = "https://arctic-shift.photon-reddit.com/api"
POST_ID_PATTERNS = (
    re.compile(r"(?:^|/)comments/(?:t3_)?([A-Za-z0-9]+)(?:/|$|[?#])", re.I),
    re.compile(r"redd\.it/(?:t3_)?([A-Za-z0-9]+)(?:/|$|[?#])", re.I),
)
ALLOWED_HOSTS = ("reddit.com", "redd.it", "reddit.app.link")


def get_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": "reddit-to-markdown/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def post_id_from_url(url: str) -> str | None:
    for pattern in POST_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1).lower()
    return None


def is_reddit_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def resolve_post_id(url: str) -> str:
    if not is_reddit_url(url):
        raise ValueError("Expected a Reddit, redd.it, or reddit.app.link URL.")
    post_id = post_id_from_url(url)
    if post_id:
        return post_id
    request = Request(url, headers={"User-Agent": "reddit-to-markdown/1.0"})
    with urlopen(request, timeout=30) as response:
        resolved_url = response.geturl()
    post_id = post_id_from_url(resolved_url)
    if not post_id:
        raise ValueError("Share URL did not resolve to a Reddit post URL. Use its canonical post URL instead.")
    return post_id


def first_data(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        data = payload.get("data", payload.get("posts", []))
    else:
        data = payload
    if not isinstance(data, list) or not data:
        raise ValueError("Archive response did not contain a post.")
    return data[0]


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def utc(value: Any) -> str:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OSError):
        return ""


def comment_url(canonical_url: str, comment_id: str) -> str:
    return canonical_url.rstrip("/") + "/" + comment_id + "/"


def normalize_comment(item: dict[str, Any], canonical_url: str) -> dict[str, Any]:
    comment_id = text(item.get("id"))
    permalink = text(item.get("permalink"))
    if permalink.startswith("/"):
        permalink = "https://www.reddit.com" + permalink
    return {
        "id": comment_id,
        "parent_id": text(item.get("parent_id")),
        "author": text(item.get("author")) or "[deleted]",
        "score": item.get("score", 0),
        "created_utc": utc(item.get("created_utc")),
        "body": text(item.get("body")),
        "url": permalink or comment_url(canonical_url, comment_id),
    }


def fetch(url: str, comment_limit: int) -> dict[str, Any]:
    post_id = resolve_post_id(url)
    post = first_data(get_json(f"{API_ROOT}/posts/ids?{urlencode({'ids': post_id})}"))
    subreddit = text(post.get("subreddit"))
    if not subreddit:
        raise ValueError("Archive response did not include a subreddit.")
    canonical_url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/"
    comments_payload = get_json(
        f"{API_ROOT}/comments/search?{urlencode({'link_id': 't3_' + post_id, 'limit': comment_limit, 'sort': 'asc'})}"
    )
    raw_comments = comments_payload.get("data", []) if isinstance(comments_payload, dict) else comments_payload
    comments = [normalize_comment(item, canonical_url) for item in raw_comments if text(item.get("id"))]
    comments.sort(key=lambda item: (item["created_utc"], item["id"]))
    return {
        "canonical_url": canonical_url,
        "subreddit": subreddit,
        "post_id": post_id,
        "post": {
            "title": text(post.get("title")),
            "author": text(post.get("author")) or "[deleted]",
            "created_utc": utc(post.get("created_utc")),
            "score": post.get("score"),
            "upvote_ratio": post.get("upvote_ratio"),
            "num_comments": post.get("num_comments"),
            "body": text(post.get("selftext")),
        },
        "comment_records": len(comments),
        "comment_limit": comment_limit,
        "comment_limit_reached": len(comments) >= comment_limit,
        "comments": comments,
    }


def quote(body: str, indent: str) -> list[str]:
    lines = body.splitlines() or [""]
    return [f"{indent}> {line}" if line else f"{indent}>" for line in lines]


def render_comments(data: dict[str, Any]) -> list[str]:
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in data["comments"]:
        children[comment["parent_id"]].append(comment)

    def visit(comment: dict[str, Any], depth: int) -> list[str]:
        indent = "  " * depth
        header = (
            f"{indent}- **u/{comment['author']}** | score: `{comment['score']}` | "
            f"UTC: `{comment['created_utc']}` | id: [`{comment['id']}`]({comment['url']})"
        )
        result = [header, *quote(comment["body"], indent + "  "), ""]
        for child in children.get("t1_" + comment["id"], []):
            result.extend(visit(child, depth + 1))
        return result

    rendered: list[str] = []
    for root in children.get("t3_" + data["post_id"], []):
        rendered.extend(visit(root, 0))
    return rendered


def render_markdown(data: dict[str, Any], include: str) -> str:
    post = data["post"]
    lines = [f"# {post['title']}", "", "## Post metadata", ""]
    lines.extend([
        f"- Subreddit: `r/{data['subreddit']}`",
        f"- Post ID: `{data['post_id']}`",
        f"- Author: `u/{post['author']}`",
        f"- Created: `{post['created_utc']}`",
        f"- Canonical URL: {data['canonical_url']}",
        f"- Post score: `{post['score']}`",
        f"- Post snapshot comments: `{post['num_comments']}`",
        f"- Archived comment records: `{data['comment_records']}`",
        "",
    ])
    if data["comment_limit_reached"]:
        lines.extend(["> Warning: the returned comment count reached `--comment-limit`; do not treat this as a complete archive.", ""])
    if include in {"post", "both"}:
        lines.extend(["## Post body", "", "```text", post["body"], "```", ""])
    if include in {"comments", "both"}:
        lines.extend(["## Comment tree", "", *render_comments(data)])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive a Reddit post and comment tree as Markdown or JSON.")
    parser.add_argument("url")
    parser.add_argument("--include", choices=("post", "comments", "both"), default="both")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--comment-limit", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.comment_limit < 1:
        parser.error("--comment-limit must be positive")
    if args.comment_limit > 100:
        parser.error("--comment-limit cannot exceed Arctic Shift's single-request maximum of 100")
    try:
        data = fetch(args.url, args.comment_limit)
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    output = json.dumps(data, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(data, args.include)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
