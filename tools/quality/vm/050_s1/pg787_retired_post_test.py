"""Literal independent preservation/foreign-change/partial-deletion vectors."""
import copy
import unittest
from pg787_retired_post import preserved


class Test(unittest.TestCase):
    def test_exact_three_only_and_all_other_values(self):
        root='/run/schubert-nk/startup';intents=[root+'/permit-start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent']
        before={'rows':{'literal':[[1,'known']]},'configuration':{'literal':'known'},'trees':{root:{root:{'metadata':[1,2,0,0,448,2,8,1,1]},root+'/epoch.current':{'sha256':'literal'},**{n:{'sha256':'literal'}for n in intents}}}}
        after=copy.deepcopy(before)
        for n in intents:after['trees'][root].pop(n)
        after['trees'][root][root]['metadata'][6:]=[4,2,2]
        self.assertTrue(preserved(before,after));self.assertFalse(preserved(before,before))
        for path in ('row','declaration','epoch','inode','extra'):
            bad=copy.deepcopy(after)
            if path=='row':bad['rows']['literal'][0][1]='foreign'
            elif path=='declaration':bad['configuration']['literal']='foreign'
            elif path=='epoch':bad['trees'][root][root+'/epoch.current']['sha256']='foreign'
            elif path=='inode':bad['trees'][root][root]['metadata'][1]=99
            else:bad['trees'][root][root+'/foreign']={}
            self.assertFalse(preserved(before,bad),path)


if __name__=='__main__':unittest.main()
