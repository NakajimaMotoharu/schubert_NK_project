"""Independent public input vectors for BUG3006's pre-write contract.

Tool PT only; no event, quota, application, backend, SDK, or held operation runs.
"""
import ast
from pathlib import Path
import unittest

from pmo_stage_input import validate_checkpoint_text


class StageCheckpointInputTest(unittest.TestCase):
    def reject(self, mode, config, message):
        with self.assertRaises(ValueError) as caught:
            validate_checkpoint_text(mode, config)
        self.assertEqual(message, str(caught.exception))

    def test_001_end_keeps_exact_unicode_and_whitespace(self):
        original = "  状態・未検証\n次command\t\n"
        config = {"checkpointText": original, "summary": "別の値"}
        self.assertEqual(original, validate_checkpoint_text("end", config))
        self.assertEqual({"checkpointText": original, "summary": "別の値"}, config)

    def test_002_start_does_not_require_end_text(self):
        self.assertIsNone(validate_checkpoint_text("start", {}))

    def test_003_summary_cannot_substitute_for_missing_checkpoint(self):
        self.reject("end", {"summary": "説明のみ"}, "nonblank end checkpointText required before mutation")

    def test_004_null_end_text(self):
        self.reject("end", {"checkpointText": None}, "nonblank end checkpointText required before mutation")

    def test_005_empty_end_text(self):
        self.reject("end", {"checkpointText": ""}, "nonblank end checkpointText required before mutation")

    def test_006_whitespace_end_text(self):
        self.reject("end", {"checkpointText": " \t\r\n\u3000"}, "nonblank end checkpointText required before mutation")

    def test_007_number_boolean_and_collection_end_text(self):
        for value in [0, 42, False, True, [], {}, ["text"]]:
            with self.subTest(value=value):
                self.reject("end", {"checkpointText": value}, "nonblank end checkpointText required before mutation")

    def test_008_unknown_modes(self):
        for mode in ["", "END", "finish", None]:
            with self.subTest(mode=mode):
                self.reject(mode, {"checkpointText": "valid"}, "registered stage mode required")

    def test_009_null_and_nonobject_config(self):
        for mode in ["start", "end"]:
            for config in [None, [], "text", 0]:
                with self.subTest(mode=mode, config=config):
                    self.reject(mode, config, "stage config object required")

    def test_010_original_bad_config_rejected_without_repair_or_mutation(self):
        config = {"summary": "保存", "nextCommand": "継続"}
        self.reject("end", config, "nonblank end checkpointText required before mutation")
        self.assertEqual({"summary": "保存", "nextCommand": "継続"}, config)

    def test_011_start_does_not_read_end_value(self):
        class UnreadEndConfig(dict):
            def get(self, key, default=None):
                raise AssertionError("start must not read end checkpointText")
        self.assertIsNone(validate_checkpoint_text("start", UnreadEndConfig()))

    def test_012_recorder_checks_input_before_persistent_mutations(self):
        path = Path("evidence/01_PT/018_NK-OPS-001/input/1100_wbs65_stage_record_v2.py")
        tree = ast.parse(path.read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        validation = [n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "validate_checkpoint_text"]
        self.assertEqual(1, len(validation))
        mutations = [n for n in calls if
                     (isinstance(n.func, ast.Name) and n.func.id in {"append_start", "write"}) or
                     (isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                      and n.func.value.id == "metrics" and n.func.attr == "append")]
        # The write function's definition is a lambda; every actual call must follow validation.
        self.assertGreaterEqual(len(mutations), 4)
        self.assertTrue(all(validation[0].lineno < n.lineno for n in mutations))
