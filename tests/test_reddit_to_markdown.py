from pathlib import Path
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
