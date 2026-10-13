import unittest
from pg2227_newboot_fresh_day_once import compose


class OnceContract(unittest.TestCase):
    def test_whole_before_actual_watch_and_original_budget(self):
        files={n:'a'*64 for n in ['pg2224_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']}
        s=compose('b'*64,files)
        for v in ['pg2226-newboot-fresh-day-before-v1','pg2227-newboot-fresh-day-once-v1',
          'PG2227-newboot-fresh-day-once-v1','b2d6f605-61cf-425f-8fbd-12d606f6ee66','PG2126',
          "frozen['existingSuccessfulInspectorStepsForDate']==0",'persist(\'external-start-guard.private.json\'',
          "'originalBudgetSeconds':1800",'systemctl\',\'start\',\'--no-block', '>=12884901888']:
            self.assertIn(v,s)
        for old in ['PG1292','pg1454','pg1455','PG1456','--resume\',','operatorInvalidIssued\':True']:
            self.assertNotIn(old,s)
        with self.assertRaises(ValueError):compose(None,files)
        with self.assertRaises(ValueError):compose('b'*64,{})


if __name__=='__main__':unittest.main()
