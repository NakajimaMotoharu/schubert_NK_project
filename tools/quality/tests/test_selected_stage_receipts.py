import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from selected_stage_receipts import verify_completed_stages


class SelectedStageReceiptsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scope = Path(temporary.name).resolve()
        self.commands = {
            "unit": ["fixed-local-ut", "--select-method", "Stub#fixed"],
            "pmd": ["fixed-pmd"],
        }
        self.accepted_exits = {"unit": (0,), "pmd": (0, 4)}
        self.golden_start = "2026-11-24T10:00:00+00:00"
        self.golden_end = "2026-11-24T10:00:01+00:00"
        for label, code in (("unit", 0), ("pmd", 4)):
            base = {"command": self.commands[label], "cwd": str(self.scope), "startUTC": self.golden_start}
            pins = {}
            for stream in ("stdout", "stderr"):
                contents = f"{label}-{stream}-fixture\n".encode()
                (self.scope / f"{label}.{stream}").write_bytes(contents)
                pins[f"{stream}Sha256"] = hashlib.sha256(contents).hexdigest()
            self.write(label, "begin", base)
            self.write(label, "process", {**base, "pid": 2, "ownerPid": 1})
            self.write(
                label,
                "exit",
                {**base, **pins, "endUTC": self.golden_end, "actualExit": code, "timedOut": False},
            )

    def write(self, label, role, record):
        path = self.scope / f"{label}-{role}.safe.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def verify(self):
        return verify_completed_stages(
            self.scope, cwd=self.scope, commands=self.commands, accepted_exits=self.accepted_exits
        )

    def test_stages001_only_complete_bound_outcomes(self):
        self.assertEqual(
            {
                "unit": {"actualExit": 0, "startUTC": self.golden_start, "endUTC": self.golden_end},
                "pmd": {"actualExit": 4, "startUTC": self.golden_start, "endUTC": self.golden_end},
            },
            self.verify(),
        )

    def test_stages002_unknown_missing_or_noncanonical_receipt(self):
        for role in ("begin", "process", "exit"):
            with self.subTest(role=role):
                self.write("other", role, {})
                with self.assertRaisesRegex(ValueError, "stage roster"):
                    self.verify()
                (self.scope / f"other-{role}.safe.json").unlink()
        expected = self.scope / "unit-exit.safe.json"
        payload = expected.read_bytes()
        expected.unlink()
        with self.assertRaisesRegex(ValueError, "exit stage roster"):
            self.verify()
        target = self.scope / "alternative-receipt.json"
        target.write_bytes(payload)
        expected.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            self.verify()
        expected.unlink()
        expected.write_bytes(payload)
        self.commands["../unknown"] = ["fixed-fixture"]
        self.accepted_exits["../unknown"] = (0,)
        with self.assertRaisesRegex(ValueError, "stage roster"):
            self.verify()

    def test_stages003_cross_scope_records_and_duplicate_fields(self):
        differences = (
            ("begin", "command", ["other-command"]),
            ("process", "cwd", "/different-cwd"),
            ("exit", "startUTC", "2026-11-24T09:00:00+00:00"),
        )
        for role, field, other in differences:
            with self.subTest(role=role, field=field):
                path = self.scope / f"unit-{role}.safe.json"
                original = json.loads(path.read_bytes())
                self.write("unit", role, {**original, field: other})
                with self.assertRaisesRegex(ValueError, "stage context"):
                    self.verify()
                self.write("unit", role, original)
        path = self.scope / "unit-process.safe.json"
        original = json.loads(path.read_bytes())
        self.write("unit", "process", {**original, "ownerPid": 3})
        with self.assertRaisesRegex(ValueError, "different process owner"):
            self.verify()
        path.write_text('{"pid":2,"pid":3}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate stage record field"):
            self.verify()

    def test_stages004_unknown_terminal_and_invalid_time(self):
        path = self.scope / "unit-exit.safe.json"
        original = json.loads(path.read_bytes())
        for changes in (
            {"actualExit": 1},
            {"actualExit": False},
            {"actualExit": None},
            {"timedOut": True},
            {"timedOut": None},
            {"endUTC": "2026-11-24T09:00:00+00:00"},
            {"endUTC": "2026-11-24T10:00:01"},
        ):
            with self.subTest(changes=changes):
                self.write("unit", "exit", {**original, **changes})
                with self.assertRaises(ValueError):
                    self.verify()

    def test_stages005_loss_or_modification_of_selected_output(self):
        for stream in ("stdout", "stderr"):
            with self.subTest(stream=stream):
                path = self.scope / f"unit.{stream}"
                old = path.read_bytes()
                path.write_bytes(b"modified\n")
                with self.assertRaisesRegex(ValueError, f"{stream} differs"):
                    self.verify()
                path.write_bytes(old)
