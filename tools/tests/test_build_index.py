import contextlib
import io
import unittest

from build_index import IndexMarkerError, expected_files, main
from tests.helpers import copy_kb, edit


class BuildIndexTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return main([*args, "--root", str(self.root)])

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    def test_secondary_topic_note_appears_in_both_topic_indexes(self):
        self.assertEqual(self.run_main(), 0)
        self.assertIn("- [Design MCP tool schemas for low token cost](schema-design.md)\n",
                      self.read("topics/mcp/README.md"))
        self.assertIn("- [Design MCP tool schemas for low token cost](../mcp/schema-design.md) (primary topic: mcp)\n",
                      self.read("topics/tool-calling/README.md"))

    def test_root_index_lists_scope_and_note_count(self):
        self.run_main()
        root_readme = self.read("README.md")
        self.assertIn("- [tool-calling](topics/tool-calling/README.md): Tool design, schemas, error handling. Notes: 2.\n",
                      root_readme)
        self.assertIn("Notes: 0.\n", root_readme)

    def test_topic_without_notes_says_so(self):
        self.run_main()
        self.assertIn("<!-- index:start -->\nNo notes yet.\n<!-- index:end -->",
                      self.read("topics/tokens-and-cost/README.md"))

    def test_check_fails_when_stale_and_passes_after_build(self):
        self.assertEqual(self.run_main("--check"), 1)
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_main("--check"), 0)

    def test_hand_edit_inside_markers_makes_check_fail(self):
        self.run_main()
        edit(self.root / "topics/mcp/README.md", "<!-- index:end -->", "- extra line\n<!-- index:end -->")
        self.assertEqual(self.run_main("--check"), 1)

    def test_missing_markers_is_an_error_not_a_silent_append(self):
        edit(self.root / "topics/mcp/README.md", "<!-- index:start -->\n", "")
        with self.assertRaises(IndexMarkerError):
            expected_files(self.root)


if __name__ == "__main__":
    unittest.main()
