"""Independent literal preservation/append classification, no live rows."""
import copy,unittest
from pg556_survivors import survivors_preserved,APPEND_ONLY


class Test(unittest.TestCase):
    def setUp(self):self.old={t:[{'id':1,'opaque':'literal','nullable':None}]for t in [*sorted(APPEND_ONLY),*[f'literal_table_{i}'for i in range(20)]]}
    def test_only_known_append_is_observed_not_accepted(self):
        self.assertEqual(survivors_preserved(self.old,self.old),{})
        new=copy.deepcopy(self.old)
        for t in APPEND_ONLY:new[t].append({'id':2,'opaque':'new-unaccepted','nullable':None})
        got=survivors_preserved(self.old,new)
        self.assertEqual(got,{t:{'addedObserved':1,'newRowsAccepted':False}for t in APPEND_ONLY})
        for t in APPEND_ONLY:
            for bad_id in(1,None,True,''):
                bad=copy.deepcopy(self.old);bad[t].append({'id':bad_id,'opaque':'other'})
                with self.assertRaises(ValueError):survivors_preserved(self.old,bad)
    def test_all24_old_changes_missing_foreign_append_null_duplicate(self):
        for t in self.old:
            bad=copy.deepcopy(self.old);bad[t][0]['opaque']='changed'
            with self.assertRaises(ValueError):survivors_preserved(self.old,bad)
            for rows in(None,[None],[{}],[],bad[t]+bad[t]):
                bad=copy.deepcopy(self.old);bad[t]=rows
                with self.assertRaises(ValueError):survivors_preserved(self.old,bad)
            if t not in APPEND_ONLY:
                bad=copy.deepcopy(self.old);bad[t].append({'id':2})
                with self.assertRaises(ValueError):survivors_preserved(self.old,bad)
        for bad in(None,{},[]):
            with self.assertRaises(ValueError):survivors_preserved(self.old,bad)


if __name__=='__main__':unittest.main()
