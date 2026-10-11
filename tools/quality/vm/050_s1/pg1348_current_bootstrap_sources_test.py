"""Whole generated sources and actual frozen schema fixture, no guest operations."""
import ast
import json
import unittest
import pg1348_current_bootstrap_sources as p
import pg1348_current_bootstrap_compile as c

class Test(unittest.TestCase):
    def test_current_sources_and_explicit_flat_abi(self):
        values = p.files('b' * 64)
        joined = '\n'.join(values.values())
        self.assertNotIn('Pg1345', joined)
        self.assertIn('Pg1348BootstrapExisting', joined)
        for name, raw in values.items():
            if name.endswith('.py'):
                ast.parse(raw)
        actual = json.loads((p.W / 'pg1335-frozen-v1.safe.json').read_bytes())['fileHashes']
        selected = {name: digest for name, digest in actual.items() if name.endswith('.class') and '/' not in name}
        self.assertGreater(len(selected), 0)
        self.assertTrue(any('/' in name for name in actual))
        for required in ('Pg387TrustedDeployment.class', 'Pg797OwnedDatabase.class', 'Pg407FailedRootRecovery.class'):
            self.assertIn(required, selected)
        self.assertIn("if name.endswith('.class') and '/' not in name:", c.source())
        self.assertIn('pg1348-frozen-v3.safe.json', c.source())

if __name__ == '__main__':
    unittest.main()
