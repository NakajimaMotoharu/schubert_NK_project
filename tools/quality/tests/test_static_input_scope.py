"""Synthetic regression cases for artifact and source input scope."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from static_input_scope import ScopeError, compare_scope, compare_source_scope, main, read_metadata


class StaticInputScopeTest(unittest.TestCase):
    def setUp(self):
        self.source = "d" * 40
        self.target = "a" * 64
        self.auxiliary = "b" * 64
        self.plan = {"source": self.source, "targets": [self.target], "auxiliaries": [self.auxiliary]}
        self.scope = {"source": self.source, "admitted": ["fixture.Main", "fixture.Aux"],
                      "held": ["fixture.Controlled", "fixture.DependsOnControlled"]}
        self.artifacts = {self.target: ["fixture.Main"], self.auxiliary: ["fixture.Aux"]}
        self.inventory = {"source": self.source, "membersByArtifactSha256": self.artifacts}

    def reject(self, reason):
        with self.assertRaisesRegex(ScopeError, "^" + reason + "$"):
            compare_scope(self.plan, self.scope, self.inventory)

    def test_exact_metadata_covers_both_roles(self):
        self.assertEqual({"targets": 1, "auxiliaries": 1, "members": 2},
                         compare_scope(self.plan, self.scope, self.inventory))

    def test_entire_target_package_includes_held_member(self):
        self.artifacts[self.target].append("fixture.Controlled")
        self.reject("HELD_MEMBER")

    def test_closed_target_with_held_transitive_auxiliary(self):
        self.artifacts[self.auxiliary].append("fixture.DependsOnControlled")
        self.reject("HELD_MEMBER")

    def test_uncatalogued_auxiliary_is_rejected(self):
        del self.artifacts[self.auxiliary]
        self.reject("UNCATALOGUED_INPUT")

    def test_unassessed_member_is_rejected(self):
        self.artifacts[self.auxiliary].append("fixture.New")
        self.reject("UNASSESSED_MEMBER")

    def test_old_scope_is_rejected_even_when_member_names_match(self):
        self.scope["source"] = "e" * 40
        self.reject("SOURCE_MISMATCH")

    def test_empty_inventory_entry_is_rejected(self):
        self.artifacts[self.target] = []
        self.reject("MISSING_OR_EMPTY_" + self.target.upper())

    def test_class_identity_shadowed_by_auxiliary_is_rejected(self):
        self.artifacts[self.auxiliary].append("fixture.Main")
        self.reject("AMBIGUOUS_MEMBER")

    def test_conflicting_metadata_is_rejected(self):
        self.scope["admitted"].append("fixture.Controlled")
        self.reject("CONTRADICTORY_SCOPE")

    def test_duplicate_json_field_is_rejected_even_with_exact_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "scope.json")
            data = b'{"admitted":["fixture.Main"],"admitted":["fixture.Other"]}'
            path.write_bytes(data)
            with self.assertRaisesRegex(ScopeError, "^DUPLICATE_FIELD$"):
                read_metadata(path, hashlib.sha256(data).hexdigest())

    def test_non_json_constants_are_rejected_even_with_exact_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "scope.json")
            for token in (b"NaN", b"Infinity", b"-Infinity"):
                with self.subTest(token=token):
                    data = b'{"observation":{"value":' + token + b'}}'
                    path.write_bytes(data)
                    with self.assertRaisesRegex(ScopeError, "^INVALID_JSON_CONSTANT$"):
                        read_metadata(path, hashlib.sha256(data).hexdigest())

    def test_cli_rejects_an_inventory_with_a_different_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, scope, inventory = [root / name for name in ("plan", "scope", "inventory")]
            plan.write_text(json.dumps(self.plan))
            scope.write_text(json.dumps(self.scope))
            inventory.write_text(json.dumps(self.inventory))
            args = [
                "--plan", str(plan), "--scope", str(scope),
                "--scope-sha256", hashlib.sha256(scope.read_bytes()).hexdigest(),
                "--inventory", str(inventory), "--inventory-sha256",
                hashlib.sha256(inventory.read_bytes()).hexdigest(),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, main(args))
            self.assertEqual({"scopeMatch": True, "targets": 1, "auxiliaries": 1, "members": 2},
                             json.loads(output.getvalue()))
            inventory.write_bytes(inventory.read_bytes() + b"\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(1, main(args))
            self.assertEqual({"scopeMatch": False, "reason": "RECEIPT_DIGEST_MISMATCH"},
                             json.loads(output.getvalue()))


class SourceInputScopeTest(unittest.TestCase):
    def setUp(self):
        self.source = "d" * 40
        self.blob = "e" * 40
        self.path = "fixture/src/Admitted.java"
        self.held = "fixture/src/Held.java"
        self.plan = {"source": self.source, "tool": "formatter", "toolSha256": "a" * 64,
                     "filesByPath": {self.path: self.blob}}
        self.scope = {"source": self.source, "tool": "formatter", "toolSha256": "a" * 64,
                      "admitted": [self.path], "held": [self.held]}
        self.inventory = {"source": self.source,
                          "filesByPath": {self.path: self.blob, self.held: "b" * 40}}

    def reject(self, reason):
        with self.assertRaisesRegex(ScopeError, "^" + reason + "$"):
            compare_source_scope(self.plan, self.scope, self.inventory)

    def test_cli_accepts_only_exact_tool_path_and_blob_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = ["--source-only"]
            for flag, record in (("plan", self.plan), ("scope", self.scope),
                                 ("inventory", self.inventory)):
                path = root / flag
                data = json.dumps(record).encode("utf-8")
                path.write_bytes(data)
                args.extend(("--" + flag, str(path)))
                if flag != "plan":
                    args.extend(("--" + flag + "-sha256", hashlib.sha256(data).hexdigest()))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, main(args))
            self.assertEqual({"scopeMatch": True, "tool": "formatter", "files": 1},
                             json.loads(output.getvalue()))

    def test_other_tool_receipt_is_rejected(self):
        self.scope["tool"] = "checkstyle"
        self.reject("TOOL_MISMATCH")

    def test_other_tool_artifact_is_rejected(self):
        self.scope["toolSha256"] = "b" * 64
        self.reject("TOOL_MISMATCH")

    def test_old_source_receipt_is_rejected(self):
        self.inventory["source"] = "f" * 40
        self.reject("SOURCE_MISMATCH")

    def test_later_held_path_invalidates_entire_batch(self):
        self.plan["filesByPath"][self.held] = "b" * 40
        self.reject("HELD_SOURCE_PATH")

    def test_unreviewed_path_is_rejected_even_when_in_inventory(self):
        extra = "fixture/src/Unreviewed.java"
        self.inventory["filesByPath"][extra] = "b" * 40
        self.plan["filesByPath"][extra] = "b" * 40
        self.reject("UNASSESSED_SOURCE_PATH")

    def test_missing_inventory_path_is_rejected(self):
        del self.inventory["filesByPath"][self.path]
        self.reject("UNCATALOGUED_SOURCE_PATH")

    def test_changed_blob_at_same_path_is_rejected(self):
        self.plan["filesByPath"][self.path] = "c" * 40
        self.reject("SOURCE_BLOB_MISMATCH")

    def test_path_aliases_and_wildcards_are_rejected_even_if_listed(self):
        for path in ("../Admitted.java", "/Admitted.java", "fixture//Admitted.java",
                     "fixture/./Admitted.java", "fixture/*", "fixture\\Admitted.java"):
            with self.subTest(path=path):
                self.plan["filesByPath"] = {path: self.blob}
                self.scope["admitted"] = [path]
                self.inventory["filesByPath"] = {path: self.blob}
                self.reject("INVALID_SOURCE_PATH")

    def test_unmodeled_arg_list_is_rejected(self):
        self.plan["inputs"] = ["fixture/src"]
        self.reject("INVALID_SOURCE_PLAN_FIELDS")


if __name__ == "__main__":
    unittest.main()
