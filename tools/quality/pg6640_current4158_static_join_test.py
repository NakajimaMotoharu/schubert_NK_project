import copy
import unittest
import pg6640_current4158_static_join as p


class StaticOriginalBindingTest(unittest.TestCase):
    def test_cross_package_component_refs_are_explicit_and_complete(self):
        row=dict(status='REQUIRED_CONTRACT',sourcePath='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/QuestionQueryRepository.java')
        classes=['dev.codex.schubert.nk.api.application.question.QuestionQueryRepositoryTest',
                 'dev.codex.schubert.nk.api.persistence.BorrowedJdbcFatal329Test']
        cases=[dict(testId='actual-'+str(i),xmlSha256='xml-'+str(i),**{'class':cls},caseNameSha256='n'+str(i),source='current') for i,cls in enumerate(classes)]
        actual=p.original_refs(row,cases,'current')
        self.assertEqual(set(classes),{c['class'] for c in actual['currentWholeCaseRefs']})
        with self.assertRaises(ValueError):p.original_refs(row,cases[:1],'current')
        with self.assertRaises(ValueError):p.original_refs(row,[dict(cases[0],**{'class':'dev.codex.schubert.nk.api.persistence.QuestionQueryRepositoryTest'})],'current')

    def test_global_ordinal_changes_keep_current_id_and_prior_rationale(self):
        old={k:'same' for k in p.SEMANTIC}
        old.update(findingId='old-global-id',rawXmlOrdinal=4,status='REQUIRED_CONTRACT',reason='individual prior rationale')
        now=dict(old,findingId='new-global-id',rawXmlOrdinal=7,status='NOT_REVIEWED_CURRENT_SOURCE')
        actual=p.rebind_unchanged(now,old)
        self.assertEqual('new-global-id',actual['findingId']);self.assertEqual(7,actual['rawXmlOrdinal'])
        self.assertEqual('old-global-id',actual['priorFindingId']);self.assertEqual(4,actual['priorRawXmlOrdinal'])
        self.assertEqual('REQUIRED_CONTRACT',actual['status']);self.assertEqual(old['reason'],actual['reason'])
        for key in p.SEMANTIC:
            with self.assertRaises(ValueError):p.rebind_unchanged(dict(now,**{key:'changed'}),old)

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
