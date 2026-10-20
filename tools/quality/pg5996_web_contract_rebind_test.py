import unittest
from pg5996_web_contract_rebind import SOURCE, require_current_facts, changed_reason


class ExplicitCurrentReasonGuardTest(unittest.TestCase):
    def test_each_type_gate_individually_zero_not_chained_comparison(self):
        good=dict(source=SOURCE,actualExit=0,compileExit=0,independentFixtureExit=0);require_current_facts(good)
        for key in ('actualExit','compileExit','independentFixtureExit'):
            for bad in (1,True,None):
                with self.assertRaises(ValueError):require_current_facts({**good,key:bad})
        with self.assertRaises(ValueError):require_current_facts({**good,'source':'old'})

    def test_no_undeclared_scope_or_wrong_owner_identity_is_reviewed(self):
        old=dict(priorReason='explicit existing reason',priorDisposition='REQUIRED_CONTRACT',plannedCurrentTestRefs=[{'class':'C','caseNameSha256':'a'*64}],currentWholeCaseRefs=[])
        row=dict(sourcePath='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/EncryptedSessionRequestCache.java',rule='CompareObjectsWithEquals',beginline='1',endline='1')
        fact=dict(path=row['sourcePath'],firstLine='1',lastLine='1',operator='NOT_EQUAL_TO',leftType='java.lang.Object',rightType='dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository',rightExpression='sessions')
        self.assertTrue(changed_reason(row,old,[],[fact])['explicitCurrentSourceRereview'])
        with self.assertRaises(ValueError):changed_reason(row,old,[],[{**fact,'rightType':'java.lang.String'}])
        with self.assertRaises(ValueError):changed_reason({**row,'rule':'Unknown'},old,[],[fact])


if __name__=='__main__':
    unittest.main()
