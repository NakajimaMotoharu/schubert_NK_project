"""Whole exports/profiles, exact after-stop baseline and no business signal/start surface."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema
import pg3038_current_runtime_retirement_dispatch as dispatch
import pg3040_current_runtime_retirement_post as post


class CurrentDispatch(unittest.TestCase):
    def test_actual_entry_retire_only_and_complete_prequalified_post(self):
        raw = dispatch.run_source()
        ast.parse(raw)
        self.assertTrue("('stage', 'retire')" in raw)
        self.assertTrue('Pg3034NativeStop retire' in raw)
        self.assertFalse('Pg3034NativeStop stop' in raw)
        self.assertTrue('pg3038-stage-v1.exit' in raw)
        self.assertTrue(dispatch.ARCHIVE in dispatch.STAGE)
        self.assertTrue('79a3260a-e16d-42bf-942a-b914ed144c28' in dispatch.STAGE)
        self.assertEqual(0, check(dispatch.post_payload(), '<complete actual stopped pre-retire post>'))
        self.assertEqual('a234e7edb4bb2c11600efce0b59f64b0097a7255663818b0f8c6d1337c01e37b', dispatch.context()[0])
        for node in ast.walk(ast.parse(raw)):
            if isinstance(node, ast.List):
                self.assertFalse({'start', 'restart', 'reset-failed', 'stop'} & {v.value for v in node.elts if isinstance(v, ast.Constant)})

    def test_complete_finite_delta_post_and_current_dependency_slots(self):
        p = json.loads((W / 'pg3012-current-resume-owned-post-v1/manifest.safe.json').read_bytes())
        raw = post.payload({n: p['proofHashes'][n]['sha256'] for n in schema.previous.SEALS})
        self.assertTrue('same_except_runtime' in raw)
        self.assertTrue('prior_equal(json.loads(prior_raw),before,after)' in raw)
        self.assertTrue('zz-pg2970-once-resume.conf' in raw)
        self.assertTrue('exactRuntimeEntryRetired' in raw)
        for old in ['pg2392', 'pg2374', 'PG2380', 'pg2380']:
            self.assertFalse(old in raw, old)


if __name__ == '__main__':
    unittest.main()
