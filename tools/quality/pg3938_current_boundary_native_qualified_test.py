"""No VM transport; mismatched bytes/source or foreign/partial streams never qualify."""
import copy
import json
import unittest
import pg3938_current_boundary_native_qualified as review


class SameSourceCachedNative(unittest.TestCase):
    def authorities(self):
        old = json.loads((review.W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())
        native = json.loads((review.W / 'pg3892-current-two-cohort-native-v1/manifest.safe.json').read_bytes())
        fixture = copy.deepcopy(old)
        fixture['result'].update(tests=3716, changedClasses=[])
        return fixture, old, native

    def test_cached_inputs_preserved_no_guest_read_or_operations(self):
        fixture, old, native = self.authorities()
        data, original = review.inputs(fixture, old, native)
        self.assertEqual(20, len(data['selected']))
        self.assertEqual(fixture['result'], data['qualifiedFull'])
        self.assertEqual(3714, old['result']['tests'])
        raw = review.server()
        self.assertIn('PG3938-native-v1', raw)
        self.assertIn('source-full-PG3928', raw)
        self.assertNotIn('source-full-PG3734', raw)
        self.assertIn("'qualified3928Tests': 3716", raw)

    def test_all_physical_source_terminal_and_stream_changes_rejected(self):
        for field in ['physical', 'source', 'terminal', 'streams', 'foreign', 'changed']:
            fixture, old, native = self.authorities()
            if field == 'physical':
                fixture['result']['allPhysicalMainSha256'] = {}
            elif field == 'source':
                fixture['result']['productionSource'] = 'a' * 40
            elif field == 'terminal':
                fixture['actualExit'] = 143
            elif field == 'streams':
                native['result']['currentNativeStreams'] = 17
            elif field == 'foreign':
                native['result']['oldNativeImported'] = True
            else:
                fixture['result']['changedClasses'] = ['unregistered-debug-byte-change']
            with self.subTest(field=field), self.assertRaises(ValueError):
                review.inputs(fixture, old, native)


if __name__ == '__main__':
    unittest.main()
