import copy
import unittest
from pg1291_held_channel_candidate_contract import MODULES,CHANGED,ADDED,verify_delta


class CandidateClassContractTest(unittest.TestCase):
    def fixtures(self):
        old={m:{'Fixture.class':'0'*64}for m in MODULES}
        old['bootstrap'].update({n:'0'*64 for n in CHANGED['bootstrap']})
        new=copy.deepcopy(old)
        new['bootstrap'].update({n:'1'*64 for n in CHANGED['bootstrap']})
        new['bootstrap'].update({n:'2'*64 for n in ADDED['bootstrap']})
        return old,new

    def test_exact_two_changes_three_nested_and_unchanged_modules(self):
        old,new=self.fixtures()
        self.assertEqual(verify_delta(old,new),11)

    def test_missing_extra_and_outer_or_other_module_changes_refused(self):
        for mode in ['missingChange','missingAdded','otherModule','extraOuter','removed','null']:
            old,new=self.fixtures()
            if mode=='missingChange':n=next(iter(CHANGED['bootstrap']));new['bootstrap'][n]=old['bootstrap'][n]
            elif mode=='missingAdded':del new['bootstrap'][next(iter(ADDED['bootstrap']))]
            elif mode=='otherModule':new['api']['Fixture.class']='3'*64
            elif mode=='extraOuter':new['bootstrap']['Extra.class']='4'*64
            elif mode=='removed':del new['web']['Fixture.class']
            else:new['batch']['Fixture.class']=None
            with self.assertRaises(ValueError):verify_delta(old,new)


if __name__=='__main__':unittest.main()
