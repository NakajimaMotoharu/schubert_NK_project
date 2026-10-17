import ast
import inspect
import unittest
from pyflakes.api import check
import pg4854_current_static_requalification as role


class NarrowAssessment(unittest.TestCase):
    def test_finding_identity_has_no_nearby_scope_fallback(self):
        row={'path':'src/schubert-nk-api/src/main/java/p/C.java','sourceSha256':'a'*64,'rule':'CompareObjectsWithEquals','priority':'3','coordinates':{'beginline':7,'endline':7,'begincolumn':1,'endcolumn':9},'message':'exact','currentAssessmentProof':{'currentOwningTests':[{'testId':'dev.codex.schubert.nk.api.p.T#normal'}]},'owningTestIds':['dev.codex.schubert.nk.api.p.T#negative'],'owningTestId':'dev.codex.schubert.nk.api.p.T#normal'}
        self.assertTrue(role.same_finding(row,dict(row)))
        for k,v in [('path','other'),('sourceSha256','b'*64),('rule','other'),('priority','2'),('coordinates',{'beginline':8}),('message','nearby')]:self.assertFalse(role.same_finding(row,{**row,k:v}))
        self.assertEqual(role.witness_ids(row),['dev.codex.schubert.nk.api.p.T#negative','dev.codex.schubert.nk.api.p.T#normal'])
        self.assertEqual([],role.witness_ids({'priorAssessment':row}))

    def test_context_is_independent_explicit_and_current_bound(self):
        row={'path':'src/schubert-nk-api/src/main/java/p/C.java','sourceSha256':'a'*64,'rule':'DoNotUseThreads'}
        ctx={'sourceSha256':{row['path']:row['sourceSha256']},'vendorExplicitJ2ee':{'DoNotUseThreads':True},'approvedDirectJavaProcess':True,'externalJavaEEManaged':False,'noManagedDeploymentDescriptors':True,'moduleRoles':{'schubert-nk-api':'STANDALONE_JAVA_SERVICE'},'architectureEvidence':['fixed approved SS311/342']}
        value=role.classify_contract(row,ctx,{})
        self.assertFalse(value['qualityGatePass']);self.assertFalse(value['rawWarningRemoved'])
        self.assertIsNone(role.classify_contract({**row,'rule':'AvoidCatchingGenericException'},ctx,{}))
        self.assertIsNone(role.classify_contract(row,{**ctx,'externalJavaEEManaged':True},{}))
        with self.assertRaises(ValueError):role.classify_contract({**row,'sourceSha256':'b'*64},ctx,{})

    def test_complete_emitted_namespace_and_held_cases(self):
        raw='\n'.join(inspect.getsource(f)for f in (role.require,role.witness_ids,role.same_finding,role.classify_contract,role.server))
        ast.parse(raw);self.assertEqual(0,check(raw,'<complete standalone source>'))
        for literal in ['NAMED_UNCHANGED_OWNING_WITNESS_REQUIRED','NO_EXACT_UNCHANGED_SOURCE_RULE_COORDINATE_MATCH','APPROVED_DESIGN_CHANGED_REQUIRES_NEW_ORACLE',"'F03Accepted':False","'rawWarningsRemoved':False"]:self.assertIn(literal,raw)


if __name__=='__main__':unittest.main()
