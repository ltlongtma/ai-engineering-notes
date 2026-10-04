import unittest
from pathlib import Path

from ste_check import check_text

FIXTURES = Path(__file__).parent / "fixtures" / "ste"


def check_fixture(name):
    return check_text((FIXTURES / name).read_text(encoding="utf-8"), name)


class SteCheckTest(unittest.TestCase):
    def test_frontmatter_and_blockquote_produce_no_finding(self):
        self.assertEqual(check_fixture("blockquote.md"), [])

    def test_passive_is_warning_outside_strict_and_error_inside(self):
        found = [(f.line, f.rule, f.severity) for f in check_fixture("passive.md")]
        self.assertEqual(found, [(1, "passive-voice", "warning"), (4, "passive-voice", "error")])

    def test_22_word_sentence_passes_outside_strict_and_fails_inside(self):
        found = [(f.line, f.rule, f.severity) for f in check_fixture("length.md")]
        self.assertEqual(found, [(4, "long-sentence", "error")])

    def test_line_number_matches_original_note(self):
        found = [(f.line, f.rule) for f in check_fixture("line-numbers.md")]
        self.assertEqual(found, [(7, "semicolon")])

    def test_unclosed_strict_block_is_an_error(self):
        found = [(f.line, f.rule, f.severity) for f in check_text("Intro.\n<!-- ste:strict -->\n1. Read the file.\n")]
        self.assertEqual(found, [(2, "strict-marker", "error")])

    def test_close_marker_without_open_marker_is_an_error(self):
        found = [(f.line, f.rule) for f in check_text("Intro.\n<!-- /ste:strict -->\n")]
        self.assertEqual(found, [(2, "strict-marker")])

    def test_marker_inside_fenced_code_is_text(self):
        text = "Use this marker:\n\n```markdown\n<!-- ste:strict -->\nThe file is deleted.\n```\n"
        self.assertEqual(check_text(text), [])

    def test_marker_inside_list_indented_fence_is_text(self):
        text = "1. Add the markers:\n\n    ```markdown\n    <!-- ste:strict -->\n    1. Open the file.\n    ```\n\n2. Save the file.\n"
        self.assertEqual(check_text(text), [])

    def test_synonym_rotation_is_warning_outside_strict_and_error_inside(self):
        flavored = check_text("Check the file. Verify the output.\n")
        self.assertEqual([(f.rule, f.severity) for f in flavored], [("synonym-rotation", "warning")])
        strict = check_text("<!-- ste:strict -->\nCheck the file. Verify the output.\n<!-- /ste:strict -->\n")
        self.assertEqual([(f.rule, f.severity) for f in strict], [("synonym-rotation", "error")])


if __name__ == "__main__":
    unittest.main()
