"""Actual receipt schema and generated precondition expression; no SSH/VM writes."""
import ast
import copy
import unittest
from pg1316_ordinary_publication_dispatch_v2 import preflight_digest,source,STAGE,BASELINE_SHA

def fixture():
    v={k:True for k in ['all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified','normalNewMetadataScopes','nativeMetadataStableTwice','startsStopsReloadsSqlWrites0']}
    v.update(actualExit=0,productionSource='d5b00104280028d9ea81b44c1d1c805f3c2861ed',formalAccepted=False,rawExported=False,proofHashes={'after.private.json':{'sha256':BASELINE_SHA,'bytes':34946179}})
    return v

class CurrentReceiptSchemaTest(unittest.TestCase):
    def test_actual_generated_precondition_and_complete_payload(self):
        code=source();compile(STAGE,'<complete sent stage>','exec')
        main=ast.parse(code).body[0]
        guard=next(n for n in main.body if isinstance(n,ast.If)and 'preflight_digest' in ast.unparse(n.test))
        expr=compile(ast.Expression(guard.test),'<actual generated precondition>','eval')
        frozen={'actualExit':0,'productionSource':fixture()['productionSource'],'genuineParentBeforeSha256':BASELINE_SHA}
        self.assertFalse(eval(expr,dict(pre=fixture(),frozen=frozen,SOURCE=fixture()['productionSource'],BEFORE=BASELINE_SHA,preflight_digest=preflight_digest)))
        self.assertNotIn('privateBeforeSha256',code)
        self.assertIn('pg1316-stage-v1.exit',code)
        self.assertIn('Pg1311OrdinaryPublication activate',code)

    def test_missing_null_false_foreign_and_bounded_proof(self):
        self.assertEqual(preflight_digest(fixture()),BASELINE_SHA)
        for key in fixture():
            for bad in [None,True if key in ['formalAccepted','rawExported']else False,'unknown']:
                v=fixture();v[key]=bad
                with self.assertRaises(ValueError):preflight_digest(v)
            v=fixture();del v[key]
            with self.assertRaises(ValueError):preflight_digest(v)
        for field,bad in [('sha256','0'*64),('bytes',0),('bytes',True),('bytes',67108865)]:
            v=fixture();v['proofHashes']['after.private.json'][field]=bad
            with self.assertRaises(ValueError):preflight_digest(v)

if __name__=='__main__':unittest.main()
