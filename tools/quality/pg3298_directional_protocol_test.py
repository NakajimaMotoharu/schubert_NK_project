import unittest
from pyflakes.api import check
import pg3298_directional_protocol_regression as related
import pg3300_directional_protocol_independent as independent


class FixedDirectionalGroupTest(unittest.TestCase):
    def test_actual_related_namespace_count_and_new_only_manifest_hash(self):
        raw = 'INPUT={}\n' + related.server()
        self.assertEqual(0, check(raw, '<related Protocol85>'))
        self.assertIn('tests==85', raw)
        self.assertIn('PG3298-v1', raw)
        self.assertIn('source-full-PG3274', raw)
        self.assertNotIn('PG3266-v1', raw)
        self.assertIn("value['serverManifestSha256']=sha(out/'manifest.safe.json')", raw)
        compile(raw, '<related85>', 'exec')

    def test_independent_has_every_actual_case_and_original_wrapper0(self):
        raw = 'INPUT={}\n' + independent.server()
        self.assertEqual(0, check(raw, '<independent Protocol85>'))
        self.assertIn("d['tests']==85", raw)
        self.assertIn("'originalWrapperExit':0", raw)
        self.assertIn('allNamedTypesHaveIndependentDirectionalFieldMeaning', raw)
        self.assertIn('PG3300-independent-directional-v1', raw)
        self.assertNotIn('PG3266-v1', raw)
        compile(raw, '<independent85>', 'exec')


if __name__ == '__main__':
    unittest.main()
