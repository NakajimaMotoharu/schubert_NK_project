"""Semantic identity must bind current physical XML, not old ordinal or historical success."""
import unittest
from collections import defaultdict
from pg5764_static_whole_join import current_reference


class CurrentCaseJoinTest(unittest.TestCase):
    def test_changed_ordinal_joins_current_not_old_xml(self):
        old={'testId':'old-id','class':'p.C','caseNameSha256':'a'*64,'xmlSha256':'old-xml'}
        current={**old,'testId':'new-id','xmlSha256':'new-xml','result':'PASS_ORIGINAL_XML'}
        index=defaultdict(list,{('p.C','a'*64):[current]});r=current_reference(old,index)
        self.assertEqual('new-id',r['testId']);self.assertEqual('new-xml',r['xmlSha256'])

    def test_missing_ambiguous_unknown_never_become_pass(self):
        old={'class':'p.C','caseNameSha256':'a'*64}
        for candidates in([], [{**old,'result':'UNKNOWN'}],[{**old,'result':'PASS_ORIGINAL_XML'}]*2):
            with self.assertRaisesRegex(ValueError,'genuine current'):current_reference(old,defaultdict(list,{('p.C','a'*64):candidates}))


if __name__=='__main__':unittest.main()
