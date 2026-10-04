import re
import unittest

from export import ExportError, export, render_md, render_mdx
from notelib import load_notes
from tests.helpers import copy_kb


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)
        self.notes = load_notes(self.root)

    def test_internal_links_point_to_note_anchors(self):
        text = render_md(self.notes, "all", self.root)
        self.assertIn('<a id="note-tool-calling-error-handling"></a>', text)
        self.assertIn("- [Handle tool errors](#note-tool-calling-error-handling)", text)
        self.assertIn("- [Design MCP tool schemas](#note-mcp-schema-design)", text)
        for target in re.findall(r"\]\(#([^)]+)\)", text):
            self.assertIn(f'<a id="{target}"></a>', text)

    def test_link_to_note_outside_the_export_becomes_text(self):
        text = render_md(self.notes, "mcp", self.root)
        self.assertIn("Handle tool errors (not in this export: topics/tool-calling/error-handling.md)", text)

    def test_note_headings_move_one_level_down(self):
        text = render_md(self.notes, "mcp", self.root)
        self.assertIn("## Design MCP tool schemas for low token cost\n", text)
        self.assertIn("\n### Summary\n", text)
        self.assertNotIn("\n## Summary\n", text)

    def test_topic_export_includes_cross_listed_notes(self):
        text = render_md(self.notes, "tool-calling", self.root)
        self.assertIn("## Handle tool errors\n", text)
        self.assertIn("## Design MCP tool schemas for low token cost\n", text)

    def test_all_export_contains_each_note_one_time(self):
        text = render_md(self.notes, "all", self.root)
        self.assertEqual(text.count('<a id="note-mcp-schema-design"></a>'), 1)
        self.assertEqual(text.count('<a id="note-tool-calling-error-handling"></a>'), 1)

    def test_mdx_escapes_braces_and_angle_brackets_outside_code(self):
        text = render_mdx(self.notes, "tool-calling", self.root)
        self.assertIn('in a \\{"is_error": true\\} result.', text)
        self.assertIn("Use a \\<tool_result> block.", text)
        self.assertIn("Keep `{braces}` in inline code.", text)
        self.assertIn('```json\n{"is_error": true}\n```', text)
        self.assertIn('A schema such as `{"type": "object"}` costs', text)
        self.assertTrue(text.startswith('---\ntitle: "AI engineering notes: tool-calling"\n---\n'))
        self.assertIn('<a id="note-mcp-schema-design"></a>', text)

    def test_unknown_topic_is_an_error(self):
        with self.assertRaises(ExportError):
            export(self.root, "md", "agents", self.root / "dist")

    def test_topic_without_notes_writes_a_short_file(self):
        path = export(self.root, "md", "tokens-and-cost", self.root / "dist")
        self.assertEqual(path.name, "tokens-and-cost.md")
        self.assertIn("No notes for this topic.", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
