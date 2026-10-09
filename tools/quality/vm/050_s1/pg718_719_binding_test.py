"""Inert exact stage/post paths, all preserved fields and no post-side mutation."""
import ast
import unittest
from pg718_stage_candidate import source as stage
from pg719_completed_post import source as post
from pg717_native import source as native


class Test(unittest.TestCase):
    def payload(self, raw):
        ast.parse(raw)
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        value = ast.literal_eval(node.value); ast.parse(value); return value

    def test_signed_unused_stage_preserves_all_current_six_private_proofs(self):
        value = self.payload(stage())
        for literal in ('pg716-completed-baseline-v1', '58154dc72379fc8a15c1d3098f75b571e14968819bec6901dfff594a6c78c029',
                        'pg715-manifest.sig', 'pg715-manifest-v1.sig', '==524', 'before=protected()',
                        'assert protected()==before', '0.1.0-PG682', '0.1.0-PG715'):
            self.assertIn(literal, value)
        for n in ('664', '702'):
            for p in ('tools', 'verify', 'existing'): self.assertIn('pg'+n+'-bootstrap-'+p+'-v1', value)

    def test_post_all21_and_current_genuine_proof(self):
        value = self.payload(post())
        for literal in ('pg717-completed-', "'PG682'if MODE=='verify'else'PG715'", "'fields':21", '==524',
                        "after['currentBootstrapProofs']", 'pg702-bootstrap-existing-v1', 'pg664-bootstrap-existing-v1',
                        'pg696-native-stop-v1', '6b3dd954959c43c1bbac2164ec9d0c6b', 'resources0'):
            self.assertIn(literal, value)
        for forbidden in ('os.replace(', 'systemctl start', 'systemctl stop', 'daemon-reload'): self.assertNotIn(forbidden, value)
        raw = native(); ast.parse(raw)
        self.assertIn('pg717-frozen-v1.safe.json', raw)
        self.assertIn("files[name] = W/'pg717-completed-tools-v1'/name", raw)
        self.assertIn('pg464-code-tools-v2', raw)


if __name__ == '__main__': unittest.main()
