"""Exact187/71 source/static closure and rejection of relaxed/foreign/incomplete evidence."""
import copy
import json
import unittest
import pg3960_literal_candidate_apply as apply


class LiteralApplication(unittest.TestCase):
    def inputs(self):
        return json.loads((apply.W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes()), json.loads((apply.W / 'pg3958-literal-candidate-static-v1/manifest.safe.json').read_bytes())

    def test_closed_cardinality_and_no_original_edit_before_apply(self):
        p, s = self.inputs(); result = apply.qualify(p, s)
        self.assertEqual(71, len(result['candidateChanges']))
        self.assertEqual(849, len(result['allCandidateSourceSha256']))
        self.assertIn("not v['MainApplied']", apply.stage_source())
        ns = apply.namespace(); self.assertTrue(callable(ns['stage'])); self.assertTrue(callable(ns['apply']))
        self.assertEqual('pg3960-literal-candidate-material-v1', ns['OUT'].name)

    def test_wrong_source_rule_delta_map_generated_scope_or_prior_application_refused(self):
        for mode in ['source', 'delta', 'map', 'generated', 'applied', 'scope', 'static']:
            p, s = self.inputs(); p, s = copy.deepcopy(p), copy.deepcopy(s)
            if mode == 'source': p['result']['baseProductionSource'] = 'a' * 40
            elif mode == 'delta': s['result']['literalDelta']['ruleCountDeltaFromBase']['CloseResource'] = -1
            elif mode == 'map': s['result']['literalDelta']['allSourceSha256'] = {}
            elif mode == 'generated': p['result']['generated70Unchanged'] = False
            elif mode == 'applied': p['result']['MainApplied'] = True
            elif mode == 'scope': p['result']['changedFiles'] = 70
            else: s['result']['checkstyle']['findings'] = 1
            with self.subTest(mode=mode), self.assertRaises(ValueError): apply.qualify(p, s)


if __name__ == '__main__':
    unittest.main()
