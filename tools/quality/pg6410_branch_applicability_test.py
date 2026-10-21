import copy
import json
import unittest
from pyflakes.api import checkPath
import pg6410_original4054_artifacts as subject
import pg6042_original3976_artifacts as reader


class BranchApplicability(unittest.TestCase):
    def fixture(self):
        source = subject.original_source(); proof = subject.branchless_proof(source)
        q = json.loads((subject.prior.BASE/'PG6402-web-frame-order-v1/manifest.json').read_bytes())
        target = {subject.KEY: {k: v for k, v in q['rawCounter'].items() if k in ('LINE', 'METHOD', 'CLASS')}}
        physical = {subject.KEY: proof[subject.KEY]['classSha256']}
        return source, target, proof, physical

    def test_actual_four_method_owner_preserves_raw_absent_branch_and_false_percentage(self):
        source, targets, proof, physical = self.fixture(); before = copy.deepcopy(targets)
        result = reader.counter_applicability(targets, proof, physical, source, 'PG6408')
        self.assertEqual(proof[subject.KEY], result[subject.KEY]['BRANCH'])
        self.assertEqual(4, proof[subject.KEY]['methodCount']); self.assertEqual([], proof[subject.KEY]['conditionalInstructions'])
        self.assertEqual(before, targets); self.assertNotIn('BRANCH', targets[subject.KEY])
        for path in (subject.__file__, reader.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_wrong_source_class_count_conditions_campaign_and_zero_injection_rejected(self):
        source, targets, proof, physical = self.fixture()
        with self.assertRaises(ValueError):
            reader.counter_applicability(targets, {}, physical, source, 'PG6408')
        for field, value in (('source', '0'*40), ('classSha256', '0'*64), ('methodCount', 3),
                             ('conditionalInstructions', ['ifnonnull']), ('rawCounterPreserved', False)):
            bad = copy.deepcopy(proof); bad[subject.KEY][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                reader.counter_applicability(targets, bad, physical, source, 'PG6408')
        for campaign in ('PG6244', 'PG9999'):
            with self.assertRaises(ValueError):
                reader.counter_applicability(targets, proof, physical, source, campaign)
        bad = copy.deepcopy(targets); bad[subject.KEY]['BRANCH'] = dict(covered=0, missed=0)
        with self.assertRaises(ValueError):
            reader.counter_applicability(bad, proof, physical, source, 'PG6408')


if __name__ == '__main__':
    unittest.main()
