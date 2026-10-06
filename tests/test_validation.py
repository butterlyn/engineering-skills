"""Small regression checks for packaging failures that HTML rendering misses."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate import validate_manifest, validate_skill


class PackagingValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.skill = Path(self.temp.name) / "example"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text(
            "---\nname: example\ndescription: Verify an example.\n---\nRead [reference](reference.md).\n",
            encoding="utf-8")
        (self.skill / "reference.md").write_text("An independently installable reference.\n", encoding="utf-8")

    def test_standalone_companion_is_valid(self):
        metadata, files = validate_skill(self.skill)
        self.assertEqual(metadata["name"], "example")
        self.assertEqual(set(files), {"SKILL.md", "reference.md"})

    def test_missing_companion_fails(self):
        (self.skill / "reference.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing reference"):
            validate_skill(self.skill)

    def test_repository_level_dependency_fails(self):
        entry = self.skill / "SKILL.md"
        entry.write_text(entry.read_text().replace("reference.md", "../README.md"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "escapes skill"):
            validate_skill(self.skill)

    def test_manifest_must_list_companions(self):
        expected = {"example": validate_skill(self.skill)}
        index = {"skills": [{"name": "example", "description": "Verify an example.", "files": ["SKILL.md"]}]}
        with self.assertRaisesRegex(ValueError, "companion"):
            validate_manifest(index, expected, lambda path: b"")

    def test_manifest_detects_changed_content(self):
        expected = {"example": validate_skill(self.skill)}
        index = json.loads('{"skills":[{"name":"example","description":"Verify an example.",'
                           '"files":["SKILL.md","reference.md"]}]}')
        with self.assertRaisesRegex(ValueError, "content differs"):
            validate_manifest(index, expected, lambda path: b"wrong content")


if __name__ == "__main__":
    unittest.main()
