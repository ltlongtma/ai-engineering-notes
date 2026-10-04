import contextlib
import io
import unittest

from build_index import IndexMarkerError, expected_files, main, overview_errors
from tests.helpers import copy_kb, edit


class BuildIndexTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return main([*args, "--root", str(self.root)])

    def run_main_output(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([*args, "--root", str(self.root)])
        return code, out.getvalue()

    def add_topic(self, name):
        folder = self.root / "topics" / name
        folder.mkdir()
        (folder / "README.md").write_text(
            f"# {name}\n\nScope: Test scope.\n\n## Notes\n\n<!-- index:start -->\n<!-- index:end -->\n",
            encoding="utf-8")

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

    def test_topic_without_overview_row_fails_until_the_row_exists(self):
        self.add_topic("agents")
        code, out = self.run_main_output()
        self.assertEqual(code, 1)
        self.assertIn("error: OVERVIEW.md: the topic folder 'topics/agents/' has no row in the topic table", out)
        self.assertIn("- [agents](topics/agents/README.md): Test scope. Notes: 0.\n", self.read("README.md"))
        self.assertEqual(self.run_main("--check"), 1)
        edit(self.root / "OVERVIEW.md", "| Capabilities | [mcp]",
             "| Orchestration | [agents](topics/agents/README.md) | Agents. |\n| Capabilities | [mcp]")
        self.assertEqual(self.run_main("--check"), 0)

    def test_prose_link_is_not_a_table_row(self):
        edit(self.root / "OVERVIEW.md", "| Capabilities | [mcp](topics/mcp/README.md) | MCP servers. |\n", "")
        self.assertEqual(overview_errors(self.root),
                         ["OVERVIEW.md: the topic folder 'topics/mcp/' has no row in the topic table"])

    def test_row_for_a_missing_topic_folder_is_an_error(self):
        edit(self.root / "OVERVIEW.md", "| Foundations | [tokens-and-cost]",
             "| Orchestration | [agents](topics/agents/README.md) | Agents. |\n| Foundations | [tokens-and-cost]")
        self.assertEqual(overview_errors(self.root),
                         ["OVERVIEW.md: a table row links 'topics/agents/README.md', but the folder does not exist"])

    def test_missing_overview_is_an_error(self):
        (self.root / "OVERVIEW.md").unlink()
        self.assertEqual(overview_errors(self.root),
                         ["OVERVIEW.md: is missing. It needs one table row for each topic folder"])
        self.assertEqual(self.run_main("--check"), 1)


if __name__ == "__main__":
    unittest.main()
