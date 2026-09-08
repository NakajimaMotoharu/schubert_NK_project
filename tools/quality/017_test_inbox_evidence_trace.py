#!/usr/bin/env python3
"""BUG-076/YKT-068: independent evidence path/hash regression, no secret fixture."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys

sys.dont_write_bytecode = True

spec = importlib.util.spec_from_file_location("collector", Path(__file__).with_name("016_collect_inbox_inspection_evidence.py"))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class EvidenceTraceTest(unittest.TestCase):
    def test_nested_reference_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix="nk-trace-") as temporary:
            root = Path(temporary)
            out = root / "004/evidence/inbox-inspection"
            out.mkdir(parents=True)
            certified = root / "008_NK-SCN-001/evidence/manifest.json"
            certified.parent.mkdir(parents=True)
            certified.write_bytes(b"{}\n")
            (out / "results.xml").write_bytes(b"<testsuite/>\n")
            manifest = {
                "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
                "fullReactorManifestSha256": hashlib.sha256(b"{}\n").hexdigest(),
                "files": [{"path": "results.xml", "sha256": hashlib.sha256(b"<testsuite/>\n").hexdigest()}],
            }
            collector.validate_trace(out, manifest, certified)
            for path in ("../../../../008_NK-SCN-001/evidence/manifest.json", "results.xml"):
                changed = copy.deepcopy(manifest)
                changed["fullReactorManifest"] = path
                with self.assertRaisesRegex(ValueError, "full reactor"):
                    collector.validate_trace(out, changed, certified)
            changed = copy.deepcopy(manifest)
            changed["fullReactorManifestSha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "full reactor"):
                collector.validate_trace(out, changed, certified)
            for path, digest in (("missing.xml", manifest["files"][0]["sha256"]),
                                 ("results.xml", "0" * 64),
                                 (manifest["fullReactorManifest"], manifest["fullReactorManifestSha256"])):
                changed = copy.deepcopy(manifest)
                changed["files"] = [{"path": path, "sha256": digest}]
                with self.assertRaisesRegex(ValueError, "local evidence"):
                    collector.validate_trace(out, changed, certified)


if __name__ == "__main__":
    unittest.main()
