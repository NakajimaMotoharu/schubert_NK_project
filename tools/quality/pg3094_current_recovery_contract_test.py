"""Latest two actor proof/TERM AST and full post normal/negative admission without mutation."""
import ast
import json
import unittest
from pyflakes.api import check
import pg3094_retained_native_schema_handoff as handoff
import pg3096_recovered_native_schema_post as post
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema


class Recovery(unittest.TestCase):
    def test_complete_exact_current_handoff(self):
        raw = handoff.payload()
        tree = ast.parse(raw)
        self.assertEqual(0, check(raw, '<whole latest handoff>'))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'terminate']
        self.assertEqual([(210935, 2505531), (210904, 2505343)], [(n.args[0].value, n.args[1].value) for n in calls])
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'SIGKILL' for n in ast.walk(tree)))
        for text in ['208849', '208880', 'pg_terminate_backend', "'daemon-reload'"]:
            self.assertTrue(text not in raw, text)
        self.assertTrue("{'refs-prepare.private.log','before.private.json'}" in raw)
        self.assertTrue('runtimeOriginalParentUnchanged' in raw)

    def test_current_raw_original_post(self):
        original = json.loads((W / 'pg3040-current-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
        seals = {n: original['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = post.payload(seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="current"\n' + raw, '<new recovery full post>'))
        for text in ['pg3094-retained-native-schema-owned-handoff-v1', 'pg3084-retained-parent-resume-preparation-v1', '210904', '210935', 'len(rows) == 24']:
            self.assertTrue(text in raw, text)


if __name__ == '__main__':
    unittest.main()
