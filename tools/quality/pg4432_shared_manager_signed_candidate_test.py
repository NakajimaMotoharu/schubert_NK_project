"""Independent prior-release inventory and fail-closed candidate gates."""
import copy
import json
import unittest
import pg4432_shared_manager_signed_candidate as tool


class SignedCandidate(unittest.TestCase):
    def test_saved_genuine_full_and_actual_prior_release_inventory_are_required(self):
        outer = json.loads((tool.W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
        gate = tool.validate_gate(outer, tool.SOURCE); self.assertTrue(tool.qualification_matches(outer))
        manifest = json.loads((tool.OLD / 'RELEASE-MANIFEST.json').read_bytes())
        before = {}
        for module in tool.prior.MODULES:
            path = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
            if path is None:
                path = next(r['path'] for r in manifest['artifacts'] if r['path'].endswith('/schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'))
            before[module] = tool.prior.class_inventory(tool.OLD / path)
        prior_gate = tool.GATE
        try:
            tool.GATE = gate; after = tool.grouped(gate['allPhysicalMainSha256'])
            self.assertEqual(1644, tool.verify_delta(before, after))
            bad = copy.deepcopy(before); bad['protocol'][next(iter(bad['protocol']))] = 'f' * 64
            with self.assertRaises(ValueError): tool.verify_delta(bad, after)
            bad = copy.deepcopy(after); bad['bootstrap'].pop('dev/codex/schubert/nk/bootstrap/SystemManagerObservation$Service.class')
            with self.assertRaises(ValueError): tool.verify_delta(before, bad)
        finally:
            tool.GATE = prior_gate

    def test_source_counts_pending_native_and_added_enum_cannot_be_relaxed(self):
        outer = json.loads((tool.W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
        for key, value in [('tests', 3717), ('mainClasses', 1643), ('global100', True), ('formalAccepted', True), ('candidateNativePending', False), ('productionSource', tool.OLD_SOURCE), ('FESFlakyNotRun', False)]:
            changed = copy.deepcopy(outer); changed['result'][key] = value
            with self.subTest(key=key):
                with self.assertRaises(ValueError): tool.validate_gate(changed, tool.SOURCE)
        raw = tool.main_source()
        self.assertIn("'tests': 3721", raw); self.assertIn("'mainClasses': 1644", raw)
        self.assertIn("'addedClasses': 1", raw)
        self.assertIn('operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar', raw)
        self.assertIn('pg4428-shared-manager-whole-qualified-v1', raw)
        self.assertNotIn('pg3968-literal-invariant-whole-qualified-v1', raw)


if __name__ == '__main__':
    unittest.main()
