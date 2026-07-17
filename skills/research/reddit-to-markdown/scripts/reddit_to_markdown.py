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
MAX_COMMENT_PAGE_SIZE = 100
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


def epoch(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None


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


def fetch_comment_pages(post_id: str, page_size: int) -> tuple[list[dict[str, Any]], int]:
    comments_by_id: dict[str, dict[str, Any]] = {}
    after: int | None = None
    page_count = 0

    while True:
        params: dict[str, str | int] = {
            "link_id": "t3_" + post_id,
            "limit": page_size,
            "sort": "asc",
        }
        if after is not None:
            params["after"] = after

        payload = get_json(f"{API_ROOT}/comments/search?{urlencode(params)}")
        page = payload.get("data", []) if isinstance(payload, dict) else payload
        if not isinstance(page, list):
            raise ValueError("Archive response did not contain a comment list.")
        if not page:
            break

        page_count += 1
        for item in page:
            comment_id = text(item.get("id")) if isinstance(item, dict) else ""
            if comment_id:
                comments_by_id[comment_id] = item

        if len(page) < page_size:
            break

        timestamps = [
            timestamp
            for item in page
            if isinstance(item, dict)
            for timestamp in [epoch(item.get("created_utc"))]
            if timestamp is not None
        ]
        if not timestamps:
            raise ValueError("Archive comments did not include pagination timestamps.")

        newest = max(timestamps)
        next_after = newest if page_size == 1 else max(0, newest - 1)
        if after is not None and next_after <= after:
            raise ValueError("Archive comment pagination did not advance; the archive may be incomplete.")
        after = next_after

    return list(comments_by_id.values()), page_count


def fetch(url: str, comment_page_size: int) -> dict[str, Any]:
    post_id = resolve_post_id(url)
    post = first_data(get_json(f"{API_ROOT}/posts/ids?{urlencode({'ids': post_id})}"))
    subreddit = text(post.get("subreddit"))
    if not subreddit:
        raise ValueError("Archive response did not include a subreddit.")
    canonical_url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/"
    raw_comments, comment_pages = fetch_comment_pages(post_id, comment_page_size)
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
            "is_self": bool(post.get("is_self")),
            "outbound_url": text(post.get("url")),
            "domain": text(post.get("domain")),
            "body": text(post.get("selftext")),
        },
        "comment_records": len(comments),
        "comment_page_size": comment_page_size,
        "comment_pages": comment_pages,
        "comment_archive_complete": True,
        "comment_limit": comment_page_size,
        "comment_limit_reached": False,
        "comments": comments,
    }


def quote(body: str, indent: str) -> list[str]:
    lines = body.splitlines() or [""]
    return [f"{indent}> {line}" if line else f"{indent}>" for line in lines]


def render_comments(data: dict[str, Any]) -> list[str]:
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    comment_ids = {comment["id"] for comment in data["comments"]}
    for comment in data["comments"]:
        children[comment["parent_id"]].append(comment)

    for siblings in children.values():
        siblings.sort(key=lambda item: (item["created_utc"], item["id"]))

    visited: set[str] = set()

    def visit(comment: dict[str, Any], depth: int) -> list[str]:
        if comment["id"] in visited:
            return []
        visited.add(comment["id"])
        indent = "  " * depth
        header = (
            f"{indent}- **u/{comment['author']}** | score: `{comment['score']}` | "
            f"UTC: `{comment['created_utc']}` | id: [`{comment['id']}`]({comment['url']}) | "
            f"parent: `{comment['parent_id']}`"
        )
        result = [header, *quote(comment["body"], indent + "  "), ""]
        for child in children.get("t1_" + comment["id"], []):
            result.extend(visit(child, depth + 1))
        return result

    rendered: list[str] = []
    root_comments = list(children.get("t3_" + data["post_id"], []))
    root_comments.extend(
        comment
        for comment in data["comments"]
        if comment["parent_id"].startswith("t1_")
        and comment["parent_id"][3:] not in comment_ids
    )
    root_comments.sort(key=lambda item: (item["created_utc"], item["id"]))
    for root in root_comments:
        rendered.extend(visit(root, 0))

    for comment in data["comments"]:
        if comment["id"] not in visited:
            rendered.extend(visit(comment, 0))
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
        f"- Post type: `{'self' if post['is_self'] else 'link'}`",
        f"- Post score: `{post['score']}`",
        f"- Post snapshot comments: `{post['num_comments']}`",
        f"- Archived comment records: `{data['comment_records']}`",
        f"- Archive pages fetched: `{data['comment_pages']}`",
        "",
    ])
    if not post["is_self"] and post["outbound_url"]:
        lines.extend([
            f"- Outbound URL: {post['outbound_url']}",
            f"- Outbound domain: `{post['domain']}`",
            "",
        ])
    if not data.get("comment_archive_complete", False):
        lines.extend(["> Warning: the archive did not return a complete comment set.", ""])
    if include in {"post", "both"}:
        lines.extend(["## Post body", ""])
        if post["body"]:
            lines.extend(["```text", post["body"], "```", ""])
        else:
            lines.extend(["_No Reddit selftext. This is a link post._", ""])
    if include in {"comments", "both"}:
        lines.extend(["## Comment tree", "", *render_comments(data)])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive a Reddit post and comment tree as Markdown or JSON.")
    parser.add_argument("url")
    parser.add_argument("--include", choices=("post", "comments", "both"), default="both")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--comment-limit",
        dest="comment_page_size",
        type=int,
        default=MAX_COMMENT_PAGE_SIZE,
        help="Comments per archive request; all pages are fetched (default: 100)",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.comment_page_size < 1:
        parser.error("--comment-limit must be positive")
    if args.comment_page_size > MAX_COMMENT_PAGE_SIZE:
        parser.error("--comment-limit cannot exceed Arctic Shift's single-request maximum of 100")
    try:
        data = fetch(args.url, args.comment_page_size)
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
