import copy
import unittest
import pg6900_current4213_delta as p


class Current4213CounterDeltaTest(unittest.TestCase):
    def fixture(self):
        def counter(missed=0):
            return {'missed': missed, 'covered': 1 - missed}
        root = {k: counter(k == 'BRANCH') for k in p.KINDS}
        gate = {k: counter(k in ('LINE', 'BRANCH')) for k in p.KINDS}
        observed = {k: counter(k in ('LINE', 'METHOD')) for k in ('LINE', 'METHOD', 'CLASS')}
        before = dict(allPhysicalMainSha256={str(i): 'fixed' for i in range(1669)},
          allActualClassCounters={p.ROOTCTX: root, p.GATE: gate, p.OBSERVED: observed},
          modules={m: {'coverage': {k: {'missed': 1, 'covered': 1} for k in p.KINDS}} for m in ('api', 'web', 'batch', 'protocol', 'storage', 'bootstrap')})
        after = copy.deepcopy(before)
        for values in after['allActualClassCounters'].values():
            for v in values.values():
                v.update(missed=0, covered=1)
        return before, after

    def test_only_two_explicit_four_closed_no_synthetic_branch(self):
        before, after = self.fixture()
        value = p.compare(before, after)
        self.assertEqual((0, 2), (value['explicitFourClosedBefore'], value['explicitFourClosedAfter']))
        self.assertNotIn('BRANCH', after['allActualClassCounters'][p.OBSERVED])
        self.assertEqual([], value['changedPhysicalMain'])

    def test_main_change_or_lost_counter_or_changed_total_rejected(self):
        for mutate in (
            lambda a: a['allPhysicalMainSha256'].update({'0': 'changed'}),
            lambda a: a['allActualClassCounters'][p.GATE]['LINE'].update(missed=1, covered=0),
            lambda a: a['allActualClassCounters'][p.OBSERVED]['METHOD'].update(missed=0, covered=2),
            lambda a: a['allActualClassCounters'][p.OBSERVED].update(BRANCH={'missed': 0, 'covered': 1})):
            before, after = self.fixture()
            mutate(after)
            with self.assertRaises(ValueError):
                p.compare(before, after)


if __name__ == '__main__':
    unittest.main()
