import unittest
from pg2133_current_normal_unused_compile import compiler,ARCHIVE,BEFORE

class ActualCompiler(unittest.TestCase):
    def test_whole_compiler_roles_real_bundle_injections_nested_graph_and_shared_bytes(self):
        raw=compiler()
        self.assertIn('pg2126-candidate-build-v1.safe.json',raw)
        self.assertIn('pg2130-current-normal-before-v1',raw)
        self.assertIn('pg2091-frozen-v1.safe.json',raw)
        self.assertIn('pg2090-current-newrun-owned-stop-tools-v1',raw)
        self.assertIn("generated['pg2132_native_refs.py'] = 'BUNDLE_HASH='",raw)
        self.assertIn("generated['pg2132_input_preflight.py'] = 'BUNDLE_HASH='",raw)
        self.assertIn('validate_actual_graph(TARGET,hashes)',raw)
        self.assertIn('inventory(TARGET)',raw)
        self.assertIn('if sha(p) != digest',raw)
        self.assertNotIn('pg1834-frozen',raw)
        self.assertNotIn('pg1849-warning',raw)
        self.assertTrue(ARCHIVE.name.startswith('pg2134-'))
        self.assertEqual(64,len(BEFORE))

if __name__=='__main__':unittest.main()
