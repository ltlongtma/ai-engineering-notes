import unittest

from check_notes import check_repo
from tests.helpers import copy_kb, edit

NOTE = "topics/mcp/schema-design.md"


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


if __name__ == "__main__":
    unittest.main()
