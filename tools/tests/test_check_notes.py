import unittest

from check_notes import check_repo
from tests.helpers import copy_kb, edit

NOTE = "topics/mcp/schema-design.md"
TOOL_FILE = "topics/tools/cli-tools.md"


class CheckNotesTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)
        self.note = self.root / NOTE

    def assertOneError(self, fragment):
        errors = check_repo(self.root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(fragment, errors[0])

    def test_fixture_has_no_errors(self):
        self.assertEqual(check_repo(self.root), [])

    def test_primary_topic_must_match_folder(self):
        edit(self.note, "topics: [mcp, tool-calling]", "topics: [tool-calling, mcp]")
        self.assertOneError("topics[0] is 'tool-calling'")

    def test_each_topic_needs_a_folder(self):
        edit(self.note, "topics: [mcp, tool-calling]", "topics: [mcp, agents]")
        self.assertOneError("the topic 'agents' has no folder")

    def test_related_link_must_resolve(self):
        edit(self.note, "../tool-calling/error-handling.md", "../tool-calling/missing.md")
        self.assertOneError("the Related link '../tool-calling/missing.md#details' does not resolve")

    def test_sources_must_not_be_empty(self):
        edit(self.note, "sources:\n  - url: https://modelcontextprotocol.io/specification\n    accessed: 2026-10-04\n",
             "sources: []\n")
        self.assertOneError("'sources' is missing or empty")

    def test_required_field_must_exist(self):
        edit(self.note, "verified_at: 2026-10-04\n", "")
        self.assertOneError("the required frontmatter field 'verified_at' is missing")

    def test_confidence_must_be_high_medium_or_low(self):
        edit(self.note, "confidence: high", "confidence: certain")
        self.assertOneError("'confidence' is 'certain'")

    def test_unverified_claim_needs_low_confidence(self):
        edit(self.note, "use fewer tokens.", "use fewer tokens (unverified).")
        self.assertOneError("contains '(unverified)'")

    def test_file_name_must_be_kebab_case(self):
        self.note.rename(self.note.with_name("Schema_Design.md"))
        edit(self.root / "topics/tool-calling/error-handling.md", "../mcp/schema-design.md", "../mcp/Schema_Design.md")
        self.assertOneError("is not kebab-case")

    def test_broken_frontmatter_is_one_error(self):
        edit(self.note, "confidence: high\n", "confidence high\n")
        self.assertOneError("frontmatter line")


    def test_tool_entry_needs_a_link_line(self):
        edit(self.root / TOOL_FILE, "- Link: https://github.com/jqlang/jq\n", "")
        self.assertOneError("the tool entry 'jq' has no 'Link:' line")

    def test_tool_entry_link_line_needs_a_value(self):
        edit(self.root / TOOL_FILE, "- Link: https://github.com/jqlang/jq\n", "- Link:\n")
        self.assertOneError("the tool entry 'jq' has no 'Link:' line")

    def test_tool_entry_needs_a_status_line(self):
        edit(self.root / TOOL_FILE, "- Status: using\n", "")
        self.assertOneError("the tool entry 'ripgrep' has no 'Status:' line with using, tried, or dropped")

    def test_tool_entry_status_must_be_one_of_three_values(self):
        for value in ("maybe", "Using", "using daily", "using | tried | dropped", ""):
            with self.subTest(value=value):
                root = copy_kb(self)
                edit(root / TOOL_FILE, "- Status: tried\n", f"- Status: {value}\n")
                errors = check_repo(root)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("the tool entry 'jq' has no 'Status:' line", errors[0])

    def test_heading_in_another_topic_is_not_a_tool_entry(self):
        edit(self.note, "## Related", "### An example heading\n\n## Related")
        self.assertEqual(check_repo(self.root), [])

if __name__ == "__main__":
    unittest.main()
