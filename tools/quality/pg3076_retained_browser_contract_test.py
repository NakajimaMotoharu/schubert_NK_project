"""Independent exact two-PID/once/no-reload recovery and all-original post scope."""
import ast
import json
import unittest
from pyflakes.api import check
import pg3074_retained_browser_full_proof as proof
import pg3076_retained_browser_owned_handoff as handoff
import pg3078_recovered_browser_post as post
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema


class Recovery(unittest.TestCase):
    def test_only_current_child_then_parent_no_other_mutation(self):
        raw = handoff.payload()
        calls = [n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'terminate']
        self.assertEqual([(208880, 2423775), (208849, 2423591)], [(n.args[0].value, n.args[1].value) for n in calls])
        self.assertIn('runtimeOriginalParentUnchanged', raw)
        self.assertIn("['31', '90']", raw)
        self.assertIn('snapshot()==snapshot()==expected[\'native\']', raw)
        self.assertIn("'replayAllowed':False", raw)
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'SIGKILL' for n in ast.walk(ast.parse(raw))))
        for old in ['119019', '118988', 'pg_terminate_backend', "'daemon-reload'"]:
            self.assertTrue(old not in raw, old)

    def test_full_current_original_post_and_hashes(self):
        old = json.loads((W / 'pg3040-current-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
        seals = {n: old['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = post.payload(seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="current"\n' + raw, '<full recovery post>'))
        for value in ['len(rows) == 24', 'pg3076-retained-browser-owned-handoff-v1', 'pg3064-browser-resume-preparation-v1', '208849', '208880', proof.FAILURE_SHA]:
            self.assertIn(value, raw)


if __name__ == '__main__':
    unittest.main()
