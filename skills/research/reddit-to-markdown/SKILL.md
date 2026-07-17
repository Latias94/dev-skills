---
name: reddit-to-markdown
description: Archive a Reddit post as Markdown. Use when given a Reddit canonical or share URL and asked to export the post body, include its comment tree, or create a faithful Chinese translation of the post and comments.
---

# Reddit to Markdown

Use `scripts/reddit_to_markdown.py` as the source of truth. It resolves a Reddit URL, fetches the archived post and comments, preserves `parent_id`, and writes normalized Markdown or JSON.

## Choose the artifact

- **Post only**: `--include post`
- **Post and comments**: `--include both`
- **Comments only**: `--include comments`
- **Chinese translation**: first write JSON, then translate the post and every comment body while preserving all metadata and the exact comment tree.

Run the script with Python 3.12+:

```powershell
python scripts/reddit_to_markdown.py <reddit-url> --include both --format markdown --output <output.md>
```

For translation, use JSON as the source artifact:

```powershell
python scripts/reddit_to_markdown.py <reddit-url> --include both --format json --output <source.json>
```

Create a second Markdown document from `source.json` using these rules:

1. Translate the title, post body, and every non-deleted comment body fully.
2. Preserve each comment's author, score, UTC time, ID, URL, parent ID, and hierarchy.
3. Do not summarize, omit, merge, reorder, or add comments.
4. State the returned comment count and the post snapshot's `num_comments` separately.

## Example

For "export this Reddit post and all comments to Markdown", run:

```powershell
python scripts/reddit_to_markdown.py https://redd.it/1usdoin --include both --output reddit-post.md
```

## Validate before handoff

1. Confirm the output post ID matches the canonical URL.
2. Confirm the Markdown or JSON comment count equals the script's `comment_records` field.
3. Treat `comment_limit_reached: true` as an incomplete archive. State the limitation and do not claim that the tree is complete.
4. For a translated artifact, confirm the set of comment IDs exactly matches the source JSON.
