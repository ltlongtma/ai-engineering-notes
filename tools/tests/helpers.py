import shutil
import tempfile
import unittest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def copy_kb(test: unittest.TestCase) -> Path:
    """Copy fixtures/kb to a temporary directory that the test removes at cleanup."""
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "kb"
    shutil.copytree(FIXTURES / "kb", root)
    return root


def edit(path: Path, old: str, new: str) -> None:
    """Replace one exact substring in a fixture copy. Fail if the substring is absent."""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{old!r} not in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
