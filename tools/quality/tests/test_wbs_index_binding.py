"""BUG-3411 / YKT-2734. Local synthetic Git indexes with no product or remote actions."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from wbs_index_binding import ACCEPTANCE, INVENTORY, validate_index


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
