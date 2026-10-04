import json
import re
import unittest

from build_site import MODAL_MAX_CHARS, SiteError, build
from tests.helpers import copy_kb, edit

STORE = re.compile(r'<script type="application/json" id="store">(.*?)</script>', re.S)


class BuildSiteTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)
        self.out = self.root / "dist" / "site"

    def read(self, rel: str) -> str:
        return (self.out / rel).read_text(encoding="utf-8")

    def store(self, rel: str) -> dict:
        return json.loads(STORE.search(self.read(rel)).group(1))

    def test_short_content_opens_in_modal_and_long_content_opens_a_page(self):
        note = self.root / "topics/tools/cli-tools.md"
        note.write_text(note.read_text(encoding="utf-8") + "\nLong text. " * MODAL_MAX_CHARS, encoding="utf-8")
        build(self.root, self.out)
        index = self.read("index.html")
        self.assertIn('<a class="card" href="topics/mcp.html" data-modal="topic:mcp">', index)
        self.assertIn('<a class="card" href="topics/tools.html">', index)
        self.assertNotIn("topic:tools", self.store("index.html"))
        self.assertIn('href="notes/tools/cli-tools.html">', self.read("topics/tools.html"))
        self.assertIn('data-modal="note:topics/mcp/schema-design.md"', self.read("topics/mcp.html"))

    def test_note_links_point_to_site_pages_that_exist(self):
        build(self.root, self.out)
        markdown = self.store("notes/mcp/schema-design.html")["note"]["md"]
        self.assertIn("[Handle tool errors](notes/tool-calling/error-handling.html#details)", markdown)
        for page in self.out.rglob("*.html"):
            for item in self.store(page.relative_to(self.out).as_posix()).values():
                for target in re.findall(r"\]\(([^)#]+)", item["md"]):
                    if not target.startswith("http"):
                        self.assertTrue((self.out / target).is_file(), f"{page}: {target}")

    def test_topic_without_overview_row_goes_to_the_other_layer(self):
        extra = self.root / "topics/extra"
        extra.mkdir()
        (extra / "README.md").write_text("# extra\n\nScope: Extra.\n", encoding="utf-8")
        build(self.root, self.out)
        index = self.read("index.html")
        self.assertIn('id="layer-other"', index)
        self.assertLess(index.index('id="layer-foundations"'), index.index('id="layer-capabilities"'))
        self.assertLess(index.index('id="layer-all-layers"'), index.index('href="topics/extra.html"'))

    def test_script_end_tag_in_a_note_does_not_end_the_store(self):
        edit(self.root / "topics/mcp/schema-design.md", "## Details", "## Details\n\nText </script> text.")
        build(self.root, self.out)
        self.assertIn("</script> text.", self.store("notes/mcp/schema-design.html")["note"]["md"])

    def test_output_folder_that_contains_the_repository_is_refused(self):
        with self.assertRaises(SiteError):
            build(self.root, self.root.parent)
        self.assertTrue((self.root / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
