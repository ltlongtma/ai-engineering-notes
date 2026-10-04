import unittest

from notelib import FrontmatterError, parse_frontmatter


class ParseFrontmatterTest(unittest.TestCase):
    def test_parses_scalars_inline_lists_and_mapping_lists(self):
        text = (
            "---\n"
            "title: Design MCP: tool schemas\n"
            "topics: [mcp, tool-calling]\n"
            "sources:\n"
            "  - url: https://example.com/a\n"
            "    accessed: 2026-10-04\n"
            "confidence: 'high'\n"
            "---\n"
            "## Summary\n"
        )
        meta, body = parse_frontmatter(text)
        self.assertEqual(meta["title"], "Design MCP: tool schemas")
        self.assertEqual(meta["topics"], ["mcp", "tool-calling"])
        self.assertEqual(meta["sources"], [{"url": "https://example.com/a", "accessed": "2026-10-04"}])
        self.assertEqual(meta["confidence"], "high")
        self.assertEqual(body, "## Summary\n")

    def test_missing_closing_line_is_an_error(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("---\ntitle: x\n## Summary\n")

    def test_unsupported_line_reports_its_line_number(self):
        with self.assertRaises(FrontmatterError) as caught:
            parse_frontmatter("---\ntitle: x\nnot a key\n---\n")
        self.assertEqual(caught.exception.line, 3)


if __name__ == "__main__":
    unittest.main()
