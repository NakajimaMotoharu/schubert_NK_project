import ast
import json
import unittest

import pg3398_retain_owner_integration as current


class IntegrationTemplates(unittest.TestCase):
    def test_native_new_suite_and_all_historical_metadata_remain_independent(self):
        def read(slot):
            return json.loads((current.W / slot / 'manifest.safe.json').read_bytes())
        full = read('pg3400-oracle-boundary-full-qualified-v1')['result']
        original = read('pg3206-expiry-group-full-qualified-v1')['result']
        capsule = read('pg3056-boundary-group-full-qualified-v1')['result']
        args = (full, original, capsule, read('pg3188-browser-native-qualified-v1')['manifestSha256'],
                read('pg3238-legacy-negative-post-v1')['capsuleSha256'],
                read('pg3214-legacy-fixture-compile-v1')['inputSha256'])
        raw = current.native_build(*args)
        tree = ast.parse(raw)
        bindings = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                    and n.targets[0].id in ['FULL', 'ORIGINAL_FULL', 'CAPSULE_FULL']}
        self.assertEqual(bindings, dict(zip(['FULL', 'ORIGINAL_FULL', 'CAPSULE_FULL'], args[:3])))
        self.assertEqual((full['tests'], full['suites']), (3707, 543))
        self.assertEqual((original['tests'], original['suites']), (3694, 542))
        self.assertEqual((capsule['tests'], capsule['suites']), (3691, 542))
        constants = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
        self.assertIn(543, constants)
        self.assertIn('PG3398', raw)
        self.assertIn('PG3402-native-join-v2', raw)
        self.assertNotIn('PG3376-native-join-v1', raw)
        with self.assertRaises(ValueError):
            current.native_build({**full, 'suites': 542}, *args[1:])
        with self.assertRaises(ValueError):
            current.native_build({**full, 'tests': 3706}, *args[1:])

    def test_actual_digest_fragments_are_never_changed(self):
        head = '3706' + 'a' * 36; digest = '3706' + 'b' * 60
        raw = current.server_source(head, digest)
        values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        self.assertIn(head, values); self.assertIn(digest, values)
        self.assertNotIn('f0' * 20, values); self.assertNotIn('e1' * 32, values)
        self.assertIn(3707, values); self.assertIn(543, values)

    def test_independent_counts_and_historical_data_are_separate(self):
        raw = current.independent_server(); tree = ast.parse(raw)
        tuples = [ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n, ast.Tuple)
                  and all(isinstance(v, ast.Constant) for v in n.elts)]
        self.assertIn((1303, 174, 568), tuples)
        self.assertNotIn((1302, 173, 568), tuples)
        compile(raw, '<fixed independent3707>', 'exec')


if __name__ == '__main__':
    unittest.main()
