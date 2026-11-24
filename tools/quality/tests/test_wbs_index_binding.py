"""BUG-3411 / YKT-2734. Local synthetic Git indexes with no product or remote actions."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from wbs_index_binding import ACCEPTANCE, INVENTORY, _GUARD, validate_index


class WbsIndexBindingTest(unittest.TestCase):
    API = "src/schubert-nk-api/src/main/java/sample/ApiType.java"
    BATCH = "src/schubert-nk-batch/src/main/java/sample/BatchType.java"

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

    def stage_product_java(self, path):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("package sample;\n")
        self.git("add", "--", path)
        return target

    def stage_roster(self, artifacts):
        value = json.dumps({"artifacts": artifacts}).encode()
        self.inventory.write_bytes(value)
        self.set_reference(value)
        self.git("add", "--", INVENTORY, ACCEPTANCE)

    def test_java_roster_reads_staged_names_and_ignores_test_paths_and_worktree_edits(self):
        old_api = self.stage_product_java(self.API)
        self.stage_product_java(self.BATCH)
        self.stage_product_java(self.API.replace("/main/", "/test/"))
        self.stage_roster(
            [
                dict(path=self.API, module="api", owner="WBS-A", costOwner="WBS-A"),
                dict(path=self.BATCH, owner="WBS-B", costOwner="WBS-B"),
                {"path": "src/deployment/example.conf"},
            ]
        )
        old_api.unlink()
        self.inventory.write_bytes(b'{"artifacts": []}')

        result = validate_index(self.root, check_java_roster=True)

        self.assertEqual(2, result["trackedJavaMain"])
        populated = {
            module: count for module, count in result["javaMainByModule"].items() if count
        }
        self.assertEqual({"api": 1, "batch": 1}, populated)

    def test_java_roster_reports_missing_and_retired_active_entries_together(self):
        self.stage_product_java(self.API)
        self.stage_roster([dict(path=self.BATCH, owner="WBS-B", costOwner="WBS-B")])

        expected = "Java roster mismatch: missing=.*ApiType.java.*obsolete=.*BatchType.java"
        with self.assertRaisesRegex(ValueError, expected):
            validate_index(self.root, check_java_roster=True)

    def test_java_roster_rejects_duplicate_ownerless_or_wrong_module_rows(self):
        self.stage_product_java(self.API)
        row = dict(path=self.API, module="api", owner="WBS-A", costOwner="WBS-A")
        cases = [
            ([row, row], "duplicate Java registration"),
            ([dict(row, owner="")], "missing Java owner"),
            ([dict(row, costOwner=None)], "missing Java costOwner"),
            ([dict(row, module="web")], "incorrect Java module registration"),
        ]
        for items, expected in cases:
            with self.subTest(expected=expected):
                self.stage_roster(items)
                with self.assertRaisesRegex(ValueError, expected):
                    validate_index(self.root, check_java_roster=True)

    def test_java_roster_rejects_symlink_without_reading_its_target(self):
        link = self.root / self.API
        link.parent.mkdir(parents=True)
        link.symlink_to("absent.java")
        self.git("add", "--", self.API)
        self.stage_roster([dict(path=self.API, owner="WBS-A", costOwner="WBS-A")])

        with self.assertRaisesRegex(ValueError, "expected one regular stage-0 Java entry"):
            validate_index(self.root, check_java_roster=True)
