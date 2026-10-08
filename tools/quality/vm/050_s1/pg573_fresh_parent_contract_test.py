import unittest
from pg573_fresh_parent_contract import prior_history, empty_oracle


class Test(unittest.TestCase):
    def test_prior_today_exact_new_run_only(self):
        rows = [{'business_date':'2026-10-07','run_id':'old','status':'SUCCESS'} for _ in range(462)] + [{'business_date':'2026-10-08','run_id':'b7e73994-b951-4696-bdd1-cfbc8a10e734','status':'SUCCESS'} for _ in range(10)]
        self.assertTrue(prior_history(rows, '2026-10-08'))
        for key, bad in [('run_id','foreign'),('status','RUNNING'),('business_date','2026-10-07')]:
            changed = [*rows[:-1], {**rows[-1],key:bad}]
            self.assertFalse(prior_history(changed,'2026-10-08'))
        for bad in (None,[],rows[:-1],[*rows,None]): self.assertFalse(prior_history(bad,'2026-10-08'))
        self.assertFalse(prior_history(rows,None))
        changed=[*rows[:-1],dict(rows[-1])];del changed[-1]['status']
        self.assertFalse(prior_history(changed,'2026-10-08'))

    def test_no_new_cleanup_targets_or_boundary_change(self):
        self.assertTrue(empty_oracle({'sessions':[],'inbox':[]},{'sessions':[],'inbox':[]}))
        for bad in (None,{},[],{'sessions':None},{'sessions':['unexpected']},{'sessions':[]}):
            self.assertFalse(empty_oracle({'sessions':[],'inbox':[]},bad))
        self.assertFalse(empty_oracle(None,None))


if __name__ == '__main__': unittest.main()
