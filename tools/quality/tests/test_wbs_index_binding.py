"""BUG-3411 / YKT-2734. Local synthetic Git indexes with no product or remote actions."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from wbs_index_binding import ACCEPTANCE, INVENTORY, _GUARD, validate_index


class WbsIndexBindingTest(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(TemporaryDirectory(prefix="wbs-index-"))
        self.root = Path(temp)
        self.git("init", "-q")
        self.inventory = self.root / INVENTORY
        self.acceptance = self.root / ACCEPTANCE
        self.inventory.parent.mkdir(parents=True)
        self.old_inventory = b'{"old": 1}\n'
        self.new_inventory = b'{"old": 1, "new": 2}\n'
        self.inventory.write_bytes(self.old_inventory)
        self.set_reference(self.old_inventory)
        self.git("add", "--", INVENTORY, ACCEPTANCE)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, timeout=10, check=True, capture_output=True)

    def set_reference(self, inventory):
        self.acceptance.write_text(json.dumps({"inventorySha256": sha256(inventory).hexdigest()}))

    def test_unchanged_staged_pair_ignores_dirty_worktree(self):
        self.inventory.write_bytes(self.new_inventory)
        self.set_reference(self.new_inventory)
        result = validate_index(self.root)
        self.assertEqual(sha256(self.old_inventory).hexdigest(), result["inventorySha256"])

    def test_partial_add_fails_even_when_worktree_hash_matches(self):
        self.inventory.write_bytes(self.new_inventory)
        self.set_reference(self.new_inventory)
        self.git("add", "--", INVENTORY)
        with self.assertRaisesRegex(ValueError, "486 inventory reference is stale"):
            validate_index(self.root)

    def test_both_matching_changes_are_admitted(self):
        self.inventory.write_bytes(self.new_inventory)
        self.set_reference(self.new_inventory)
        self.git("add", "--", INVENTORY, ACCEPTANCE)
        self.assertEqual(
            sha256(self.new_inventory).hexdigest(), validate_index(self.root)["inventorySha256"]
        )

    def test_missing_staged_snapshot_is_reported(self):
        self.git("rm", "-f", "--", ACCEPTANCE)
        with self.assertRaisesRegex(ValueError, "expected one staged WBS blob"):
            validate_index(self.root)

    def test_non_json_constants_are_rejected_at_both_publication_entry_points(self):
        verify_files = _GUARD["verify_files"]
        for doc in ("inventory", "acceptance"):
            for token in (b"NaN", b"Infinity", b"-Infinity"):
                inventory = self.old_inventory
                if doc == "inventory":
                    inventory = b'{"observed": ' + token + b"}\n"
                self.inventory.write_bytes(inventory)
                if doc == "acceptance":
                    expected = sha256(inventory).hexdigest().encode()
                    self.acceptance.write_bytes(
                        b'{"inventorySha256": "' + expected + b'", "observed": ' + token + b"}\n"
                    )
                else:
                    self.set_reference(inventory)
                self.git("add", "--", INVENTORY, ACCEPTANCE)
                for check in (verify_files, validate_index):
                    with self.subTest(document=doc, literal=token.decode(), entry=check.__name__):
                        with self.assertRaisesRegex(ValueError, "non-JSON numeric constant"):
                            check(self.root)
