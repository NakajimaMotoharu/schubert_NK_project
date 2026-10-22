import copy
import json
import unittest
import pg6818_current_counter_delta as p


class CounterDeltaDefinitionTest(unittest.TestCase):
    def test_absent_zero_missed_or_covered_not_implicitly100(self):
        c={k:dict(covered=1,missed=0)for k in p.KINDS};self.assertTrue(p.explicit_four100(c))
        for kind in p.KINDS:
            for bad in ({k:v for k,v in c.items()if k!=kind},dict(c,**{kind:dict(covered=0,missed=0)}),dict(c,**{kind:dict(covered=1,missed=1)})):
                self.assertFalse(p.explicit_four100(bad))

    def test_real_frozen_baseline_rejects_unchanged_or_deleted_or_unrelated(self):
        before=json.loads(p.BEFORE.read_bytes())
        with self.assertRaises(ValueError):p.compare(before,before)
        after=copy.deepcopy(before);del after['allPhysicalMainSha256'][next(iter(after['allPhysicalMainSha256']))]
        with self.assertRaises(ValueError):p.compare(before,after)


if __name__=='__main__':unittest.main()
