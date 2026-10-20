import copy
import unittest
import pg5936_monitor_baseline_coverage as t


class BoundedOriginalMetadataTest(unittest.TestCase):
    def fixture(self):
        name = 'dev/codex/schubert/nk/api/Fixture'
        q = {'serverManifestSha256': 'a'*64, 'modules': {'api': {'coverageXmlSha256': 'b'*64, 'unused': 'SHOULD_NOT_SEND'*30000}},
             'allPhysicalMainSha256': {'api:'+name+'.class': 'c'*64, 'other': 'SHOULD_NOT_SEND'*30000}}
        return q, [{'module': 'api', 'class': name}]

    def test_unused_full_metadata_never_enters_bounded_same_verification(self):
        q, targets = self.fixture(); raw = t.bounded_reader(q, targets)
        self.assertLess(len(raw.encode()), 32768); self.assertNotIn('SHOULD_NOT_SEND', raw)
        self.assertIn('a'*64, raw); self.assertIn('b'*64, raw); self.assertIn('c'*64, raw)
        self.assertIn('actual current Main class byte identity', raw)
        self.assertIn('actual original XML hash', raw)

    def test_missing_duplicate_bad_hash_module_or_path_is_rejected(self):
        q, targets = self.fixture()
        for value in ([], targets+targets, [{'module': 'foreign', 'class': targets[0]['class']}], [{'module': 'api', 'class': '../../outside'}]):
            with self.assertRaises(ValueError):
                t.bounded_reader(q, value)
        bad = copy.deepcopy(q); bad['allPhysicalMainSha256'] = {}
        with self.assertRaises(ValueError):
            t.bounded_reader(bad, targets)
        bad = copy.deepcopy(q); bad['modules']['api']['coverageXmlSha256'] = 'UNKNOWN'
        with self.assertRaises(ValueError):
            t.bounded_reader(bad, targets)

    def test_oversized_but_unique_target_metadata_fails_before_transport(self):
        q, _targets = self.fixture(); targets = []
        for i in range(64):
            name = 'dev/codex/schubert/nk/api/'+'A'*600+str(i)
            targets.append({'module': 'api', 'class': name}); q['allPhysicalMainSha256']['api:'+name+'.class'] = 'd'*64
        with self.assertRaisesRegex(ValueError, 'before SSH'):
            t.bounded_reader(q, targets)


if __name__ == '__main__':
    unittest.main()
