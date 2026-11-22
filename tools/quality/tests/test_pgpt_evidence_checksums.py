"""Local evidence fixtures for BUG-3601 / YKT-2833."""
import importlib.util
import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from pgpt_evidence_checksums import write_scope_checksums


def load_scope_validator():
    script = Path(__file__).resolve().parents[1] / "018_collect_verified_evidence_set.py"
    spec = importlib.util.spec_from_file_location("verified_evidence_set", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_scope


ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VALIDATE_SCOPE = load_scope_validator()


class EvidenceChecksumTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.scope = self.root / "scope"
        (self.scope / "a").mkdir(parents=True)
        (self.scope / "a" / "detail.txt").write_bytes(b"abc")
        (self.scope / "a-file.txt").write_bytes(b"")
        self.files = [
            dict(path="a/detail.txt", sha256=ABC),
            dict(path="a-file.txt", sha256=EMPTY),
        ]
        self.manifest = self.scope / "manifest.json"
        self.manifest.write_text(json.dumps(dict(
            runId="run", targetCommit="commit", branch="branch", exitCode=0, files=self.files,
        )), encoding="utf-8")
        self.checksums = self.scope / "checksums.sha256"
        self.root_digest = sha256(self.manifest.read_bytes()).hexdigest()

    def validate(self):
        return VALIDATE_SCOPE(self.root, "scope", "run", "commit", "branch")

    def assert_exact_inventory(self):
        self.assertEqual(
            f"{ABC}  a/detail.txt\n{EMPTY}  a-file.txt\n{self.root_digest}  manifest.json\n",
            self.checksums.read_text(encoding="utf-8"),
        )
        self.assertEqual(dict(scope="scope", manifestSha256=self.root_digest), self.validate())

    def test_clean_scope_preserves_paths_and_checksum_order(self):
        write_scope_checksums(self.scope, self.files)
        self.assert_exact_inventory()

    def test_nested_manifests_and_checksum_notes_keep_their_own_scope(self):
        (self.scope / "a" / "manifest.json").write_bytes(b"{}\n")
        (self.scope / "a" / "checksums.sha256").write_bytes(b"provisional checksum note\n")
        write_scope_checksums(self.scope, self.files)
        self.assert_exact_inventory()

    def test_missing_checksum_file_entry_still_fails_validation(self):
        write_scope_checksums(self.scope, self.files)
        text = self.checksums.read_text(encoding="utf-8")
        self.checksums.write_text(text.replace(f"{ABC}  a/detail.txt\n", ""), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "^incomplete checksum inventory$"):
            self.validate()

    def test_changed_evidence_still_fails_validation(self):
        write_scope_checksums(self.scope, self.files)
        (self.scope / "a" / "detail.txt").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "^evidence file hash mismatch$"):
            self.validate()
