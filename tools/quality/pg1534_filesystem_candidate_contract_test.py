"""Handwritten class-delta oracle, never inferred from candidate differences."""
import copy
import unittest
from pg1534_filesystem_candidate_contract import MODULES, CHANGED, ADDED, verify_delta

class DeltaTest(unittest.TestCase):
    def fixtures(self):
        old = {m: {'Unchanged.class': '0' * 64} for m in MODULES}
        old['batch'].update({n: '0' * 64 for n in CHANGED['batch']})
        new = copy.deepcopy(old)
        new['batch'].update({n: '1' * 64 for n in CHANGED['batch']})
        new['storage'].update({n: '2' * 64 for n in ADDED['storage']})
        return old, new

    def test_fixed_delta(self):
        old, new = self.fixtures()
        self.assertEqual(verify_delta(old, new), 12)

    def test_unknown_missing_removed_null_and_foreign(self):
        for kind in ['changeMissing', 'addMissing', 'extra', 'removed', 'null', 'foreign']:
            with self.subTest(kind=kind):
                old, new = self.fixtures()
                if kind == 'changeMissing':
                    n=next(iter(CHANGED['batch']));new['batch'][n]=old['batch'][n]
                elif kind == 'addMissing':del new['storage'][next(iter(ADDED['storage']))]
                elif kind == 'extra':new['storage']['Foreign.class']='3'*64
                elif kind == 'removed':del new['api']['Unchanged.class']
                elif kind == 'null':new['web']['Unchanged.class']=None
                else:new['protocol']['Unchanged.class']='4'*64
                with self.assertRaises(ValueError):verify_delta(old,new)

if __name__ == '__main__':unittest.main()
