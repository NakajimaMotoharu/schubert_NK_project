import copy
import unittest
import pg6640_current4158_static_join as p


class StaticOriginalBindingTest(unittest.TestCase):
    def test_same_source_case_rebind_without_old_success_transfer(self):
        case=dict(testId='current',xmlSha256='current-xml',**{'class':'C'},caseNameSha256='n',source='new')
        row=dict(status='REQUIRED_CONTRACT',priorCurrentRefs=[dict(case,source='old')])
        old=copy.deepcopy(row);actual=p.original_refs(row,[case],'new')
        self.assertEqual(old,row);self.assertEqual('new',actual['currentWholeCaseRefs'][0]['source'])
        self.assertFalse(actual['historicalSuccessImported']);self.assertFalse(actual['F03Accepted'])
        with self.assertRaises(ValueError):p.original_refs(row,[],'new')
        with self.assertRaises(ValueError):p.original_refs(row,[dict(case,source='old')],'new')

    def test_unreviewed_is_never_promoted_by_whole(self):
        row=dict(status='NOT_REVIEWED_CURRENT_SOURCE',reviewHold='held')
        self.assertIs(row,p.original_refs(row,[],'new'))

    def test_unknown_changed_scope_not_default_approved(self):
        with self.assertRaises(ValueError):p.review_changed(dict(sourcePath='Unknown.java'))


if __name__=='__main__':unittest.main()
