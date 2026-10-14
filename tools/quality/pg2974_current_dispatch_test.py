"""Completed source/stage/post boundary; no actual guest operation in tests."""
import ast
import json
import unittest
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema
import pg2974_current_resume_dispatch as dispatch
import pg2976_current_resume_independent_post as post


class CompleteDispatch(unittest.TestCase):
    def test_new_only_whole_stage_and_action(self):
        for raw in [dispatch.source(), dispatch.STAGE]:
            ast.parse(raw)
            for old in ['pg2950', 'pg2952', 'pg2954', 'pg2306', 'b2d6f605']:
                self.assertFalse(old in raw, old)
        self.assertTrue('pg2972-frozen' in dispatch.source())
        self.assertTrue('Pg2970FreshResumePreparation' in dispatch.source())
        self.assertTrue(dispatch.TOOLS in dispatch.STAGE)

    def test_independent_literal_whole_post(self):
        old = json.loads((W / 'pg2940-current-resume-before-v1/manifest.safe.json').read_bytes())
        seals = {n: old['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = post.payload(seals)
        for token in ['len(rows) == 24', 'metadata-clock-lower.private.json', 'zz-pg2970-once-resume.conf', 'pg2974-current-cold-resume-preparation-v1', '0dc63b79-3f9a-450c-b2a6-56f86272d272']:
            self.assertTrue(token in raw, token)
        for old in ['pg2950', 'pg2954', 'PG2956']:
            self.assertFalse(old in raw, old)
        self.assertTrue("if k not in {'configuration','runtime'}" in raw)
        self.assertTrue('normalSingleRuntimeReload=true' in raw)


if __name__ == '__main__':
    unittest.main()
