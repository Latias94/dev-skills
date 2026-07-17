from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "skills" / "research" / "reddit-to-markdown" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import reddit_to_markdown


class PostIdFromUrlTests(unittest.TestCase):
    def test_canonical_post_url(self):
        self.assertEqual(
            reddit_to_markdown.post_id_from_url("https://www.reddit.com/r/bevy/comments/1usdoin/title/"),
            "1usdoin",
        )

    def test_global_post_url(self):
        self.assertEqual(
            reddit_to_markdown.post_id_from_url("https://old.reddit.com/comments/1usdoin/?rdt=42"),
            "1usdoin",
        )

    def test_comment_permalink(self):
        self.assertEqual(
            reddit_to_markdown.post_id_from_url("https://www.reddit.com/r/bevy/comments/1usdoin/title/ownenav/"),
            "1usdoin",
        )

    def test_reddit_short_id(self):
        self.assertEqual(reddit_to_markdown.post_id_from_url("https://redd.it/1usdoin"), "1usdoin")

    def test_rejects_non_post_url(self):
        self.assertIsNone(reddit_to_markdown.post_id_from_url("https://www.reddit.com/r/bevy/s/SbuSjGhY0V"))


class CommentPaginationTests(unittest.TestCase):
    @patch.object(reddit_to_markdown, "get_json")
    def test_fetches_all_comment_pages_with_overlap_and_deduplication(self, get_json):
        post = {
            "data": [
                {
                    "id": "post1",
                    "subreddit": "rust",
                    "title": "Title",
                    "author": "author",
                    "created_utc": 1,
                    "num_comments": 3,
                    "is_self": False,
                    "url": "https://example.com/article",
                    "domain": "example.com",
                    "selftext": "Body",
                }
            ]
        }
        first_page = {
            "data": [
                {"id": "a", "parent_id": "t3_post1", "created_utc": 10, "body": "A"},
                {"id": "b", "parent_id": "t3_post1", "created_utc": 20, "body": "B"},
            ]
        }
        second_page = {
            "data": [
                {"id": "b", "parent_id": "t3_post1", "created_utc": 20, "body": "B"},
                {"id": "c", "parent_id": "t1_b", "created_utc": 30, "body": "C"},
            ]
        }
        final_overlap = {
            "data": [
                {"id": "c", "parent_id": "t1_b", "created_utc": 30, "body": "C"},
            ]
        }
        get_json.side_effect = [post, first_page, second_page, final_overlap]

        data = reddit_to_markdown.fetch(
            "https://www.reddit.com/r/rust/comments/post1/title/",
            comment_page_size=2,
        )

        self.assertEqual(data["comment_records"], 3)
        self.assertEqual(data["comment_pages"], 3)
        self.assertTrue(data["comment_archive_complete"])
        self.assertFalse(data["comment_limit_reached"])
        self.assertFalse(data["post"]["is_self"])
        self.assertEqual(data["post"]["outbound_url"], "https://example.com/article")
        self.assertEqual([comment["id"] for comment in data["comments"]], ["a", "b", "c"])
        comment_urls = [call.args[0] for call in get_json.call_args_list[1:]]
        after_values = [parse_qs(urlparse(url).query).get("after") for url in comment_urls]
        self.assertEqual(after_values, [None, ["19"], ["29"]])

    def test_render_includes_parent_ids_and_orphaned_replies(self):
        data = {
            "post_id": "post1",
            "comments": [
                {
                    "id": "root",
                    "parent_id": "t3_post1",
                    "author": "one",
                    "score": 1,
                    "created_utc": "2024-01-01 00:00:00 UTC",
                    "body": "Root",
                    "url": "https://reddit.com/root",
                },
                {
                    "id": "orphan",
                    "parent_id": "t1_missing",
                    "author": "two",
                    "score": 2,
                    "created_utc": "2024-01-01 00:01:00 UTC",
                    "body": "Orphan",
                    "url": "https://reddit.com/orphan",
                },
            ],
        }

        rendered = "\n".join(reddit_to_markdown.render_comments(data))

        self.assertIn("parent: `t3_post1`", rendered)
        self.assertIn("parent: `t1_missing`", rendered)
        self.assertIn("Root", rendered)
        self.assertIn("Orphan", rendered)


if __name__ == "__main__":
    unittest.main()
