import copy
import unittest
import pg6940_current4222_delta as p


class Current4222CounterDeltaTest(unittest.TestCase):
    def fixture(self):
        keys = sorted(p.TARGETS)
        values = {k: {t: dict(missed=1, covered=1) for t in p.KINDS if t != 'BRANCH' or 'Receipt.class' in k} for k in keys}
        before = dict(allPhysicalMainSha256={str(i): 'same' for i in range(1669)}, allActualClassCounters=values,
          modules={m: {'coverage': {t: dict(missed=1, covered=1) for t in p.KINDS}} for m in ('api', 'web', 'batch', 'protocol', 'storage', 'bootstrap')})
        after = copy.deepcopy(before)
        for row in after['allActualClassCounters'].values():
            for v in row.values():
                v.update(missed=0, covered=2)
        return before, after

    def test_branchless_not_four_positive_closure(self):
        before, after = self.fixture()
        value = p.compare(before, after)
        self.assertEqual((0, 1), (value['explicitFourClosedBefore'], value['explicitFourClosedAfter']))
        self.assertEqual(3, len(value['changedCounters']))

    def test_source_or_counter_manipulation_rejected(self):
        key = sorted(p.TARGETS)[0]
        for mutate in (
          lambda a: a['allPhysicalMainSha256'].update({'0': 'different'}),
          lambda a: a['allActualClassCounters'][key].update(BRANCH=dict(missed=0, covered=2)),
          lambda a: a['allActualClassCounters'][key]['LINE'].update(missed=2, covered=0),
          lambda a: a['allActualClassCounters'][key]['LINE'].update(missed=0, covered=3),
          lambda a: a['allActualClassCounters'].update(unrelated={'LINE': dict(missed=0, covered=1)})):
            before, after = self.fixture()
            mutate(after)
            with self.assertRaises(ValueError):
                p.compare(before, after)


if __name__ == '__main__':
    unittest.main()
