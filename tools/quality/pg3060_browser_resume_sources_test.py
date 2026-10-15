"""Independent latest positive tuple and all historical rejection identities retained."""
import ast
import unittest
import pg2970_current_resume_sources as previous
from pg2970_current_resume_sources_test import wrapper
import pg3060_browser_resume_sources as current


class Latest(unittest.TestCase):
    def test_current_binding_and_foreign_denials_are_separate(self):
        values = current.sources()
        self.assertEqual(20, len(values))
        raw = values['pg3060_parent_receipt.py']
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BINDING' for t in n.targets))
        expected = {'activation': '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf', 'boot': '79a3260ae16d42bf942ab914ed144c28', 'cutoff': '2026-10-14T19:12:28.842213Z', 'invocation': '65ad6798d497474685fa32d6750cea1f', 'job': '35795', 'run': '0dc63b79-3f9a-450c-b2a6-56f86272d272', 'start': 18100986959}
        self.assertEqual(expected, ast.literal_eval(node.value))
        classify = wrapper(raw)
        self.assertEqual('DELEGATED_TO_REAL_CONTRACT', classify(expected, None, [], b''))
        for run in ['4148e3e8-f107-431a-ab27-d6e6d1f1772e', 'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75', '06236d14-a6f8-4d05-a6ff-49c713cc2647', '91f5484b-9702-4c7c-97f3-dd5110a853f9']:
            with self.assertRaises(ValueError):
                classify({'run': run}, None, [], b'')
        for activation in ['e31b627c-c0e2-4120-bd64-c0777479e800', '9026b2ab-bb42-49cd-a2bd-4c661049dce3', 'c347b14a-2e59-41e6-993c-a07e537cbd00', 'e1429ac8-f3dd-4e8c-83d2-1926c4ba8440']:
            with self.assertRaises(ValueError):
                classify({'activation': activation}, None, [], b'')
        for suffix in previous.HELPERS:
            self.assertEqual(current.bind(previous.sources()['pg2970_' + suffix]), values['pg3060_' + suffix])
        refs = values['pg3060_native_refs.py']
        for literal in [current.BEFORE, 'pg3034-native-stop-v1/after.private.json', 'END = 19749542200', 'START = 18100986959', 'metadata_lower_ns()']:
            self.assertIn(literal, refs)
        for name, value in values.items():
            self.assertNotIn('pg2970', name)
            self.assertNotIn('74729e17-91c0-43e7-b01f-74f9e6461d6a', value)


if __name__ == '__main__':
    unittest.main()
