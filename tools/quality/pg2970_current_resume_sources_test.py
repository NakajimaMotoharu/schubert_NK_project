"""Independent literal current/forbidden tuples; regression for generic bind damage."""
import ast
import unittest
import pg2890_network_owned_sources as qualified
import pg2950_current_cold_resume_sources as failed
import pg2970_current_resume_sources as current


def wrapper(raw):
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'classify')
    scope = {'_normal_classify': lambda binding, state, rows, done: 'DELEGATED_TO_REAL_CONTRACT'}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<independent boundary oracle>', 'exec'), scope)
    return scope['classify']


class CurrentHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = current.sources()

    def test_failed_generator_rejects_real_current_tuple(self):
        classify = wrapper(failed.sources()['pg2950_parent_receipt.py'])
        with self.assertRaisesRegex(ValueError, 'old-source completion'):
            classify({'run': '0dc63b79-3f9a-450c-b2a6-56f86272d272', 'activation': '74729e17-91c0-43e7-b01f-74f9e6461d6a'}, None, [], b'')

    def test_current_tuple_delegates_not_fabricates_success(self):
        classify = wrapper(self.values['pg2970_parent_receipt.py'])
        self.assertEqual('DELEGATED_TO_REAL_CONTRACT', classify({'run': '0dc63b79-3f9a-450c-b2a6-56f86272d272', 'activation': '74729e17-91c0-43e7-b01f-74f9e6461d6a'}, None, [], b''))

    def test_all_historical_runs_and_activations_still_rejected(self):
        classify = wrapper(self.values['pg2970_parent_receipt.py'])
        for run in ['4148e3e8-f107-431a-ab27-d6e6d1f1772e', 'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75', '06236d14-a6f8-4d05-a6ff-49c713cc2647', '91f5484b-9702-4c7c-97f3-dd5110a853f9']:
            with self.subTest(run=run), self.assertRaises(ValueError):
                classify({'run': run}, None, [], b'')
        for activation in ['e31b627c-c0e2-4120-bd64-c0777479e800', '9026b2ab-bb42-49cd-a2bd-4c661049dce3', 'c347b14a-2e59-41e6-993c-a07e537cbd00', 'e1429ac8-f3dd-4e8c-83d2-1926c4ba8440']:
            with self.subTest(activation=activation), self.assertRaises(ValueError):
                classify({'activation': activation}, None, [], b'')

    def test_all_six_helpers_exact_namespace_only(self):
        old = qualified.sources()
        self.assertEqual(20, len(self.values))
        for suffix in current.HELPERS:
            expected = old['pg2890_' + suffix].replace('pg2890', 'pg2970').replace('Pg2890', 'Pg2970').replace('PG2890', 'PG2970')
            self.assertTrue(expected == self.values['pg2970_' + suffix], suffix)
        self.assertIn('mutation_begin_ns=metadata_lower_ns()', self.values['pg2970_native_refs.py'])
        for name in self.values:
            self.assertNotIn('pg2950', name)


if __name__ == '__main__':
    unittest.main()
