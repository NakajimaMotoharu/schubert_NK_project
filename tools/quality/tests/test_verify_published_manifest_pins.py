import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from verify_published_manifest_pins import audit


FIXTURE = "src/example.txt"
MANIFEST = "evidence/01_PT/001_fixture/evidence/manifest.json"
INITIAL = b"independent original sample\n"
UPDATED = b"independent revised sample\n"


def pin(path, expected, **fields):
    return {"path": str(path), "sha256": hashlib.sha256(expected).hexdigest(), **fields}


class PublishedManifestPinsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.git("init", "-q")
        self.write(FIXTURE, INITIAL)
        self.original = self.commit()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
            cwd=self.repo,
            stderr=subprocess.PIPE,
            text=True,
        ).strip()

    def write(self, name, content):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def manifest(self, value, name=MANIFEST):
        self.write(name, json.dumps(value).encode())

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture revision")
        return self.git("rev-parse", "HEAD")

    def test_exact_source_can_precede_the_current_range(self):
        self.write(FIXTURE, UPDATED)
        start = self.commit()
        self.manifest(
            {
                "inputs": [
                    pin(FIXTURE, INITIAL, source=self.original),
                    pin(self.repo / FIXTURE, UPDATED),
                    pin("../local-only.txt", b"external synthetic"),
                    pin("program/characterization/baseline/current/fixture.txt", INITIAL),
                ]
            }
        )
        end = self.commit()

        result = audit(self.repo, start, end)

        self.assertEqual(1, result["manifests"])
        self.assertEqual(1, result["current"])
        self.assertEqual(1, result["historical"])
        self.assertEqual(2, result["externalOrProtected"])
        self.assertEqual([], result["unresolved"])

    def test_named_source_requires_its_own_hash(self):
        self.write(FIXTURE, UPDATED)
        self.manifest({"nested": pin(FIXTURE, UPDATED, source=self.original)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual(0, result["current"])
        self.assertEqual(
            [{"manifest": MANIFEST, **pin(FIXTURE, UPDATED, source=self.original)}],
            result["unresolved"],
        )

    def test_current_tree_is_from_commit_and_never_from_worktree(self):
        self.manifest([pin(FIXTURE, INITIAL), pin(FIXTURE, INITIAL)])
        self.manifest([pin(FIXTURE, UPDATED)], "documents/manifest.json")
        end = self.commit()
        self.write(FIXTURE, UPDATED)

        result = audit(self.repo, self.original, end)

        self.assertEqual(1, result["manifests"])
        self.assertEqual(1, result["current"])
        self.assertEqual([], result["unresolved"])

    def test_implicit_reference_uses_its_published_history(self):
        self.write(FIXTURE, UPDATED)
        self.commit()
        self.write(FIXTURE, b"third version\n")
        self.manifest({"reference": pin(FIXTURE, UPDATED)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual(1, result["historical"])
        self.assertEqual([], result["unresolved"])

    def test_missing_path_is_reported_and_invalid_commit_is_rejected(self):
        self.manifest({"reference": pin("src/absent.txt", INITIAL)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual("src/absent.txt", result["unresolved"][0]["path"])
        with self.assertRaises(ValueError):
            audit(self.repo, "HEAD", end)


if __name__ == "__main__":
    unittest.main()
