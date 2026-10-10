import ast
import copy
import unittest
from pg1148_native_five_sources import files, BASE, SHA
from pg1148_native_five_policy import coverage_delta, COVERAGE


class NativeFiveTest(unittest.TestCase):
    def test_source_fixed_five_and_all_scope_closure(self):
        values=files();java=values['Pg1148NativeRolePreparation.java'];refs=values['pg1148_native_role_refs.py'];ast.parse(refs)
        for literal in ['0.1.0-PG1068','343a5a1b-d064-47d5-88c2-31c36d7ba7a4','prepareParent(common)','nativeRoles5Prepared','db.rollback();db.close()','refs.release()','root.close()']:
            self.assertTrue(literal in java,literal)
        for literal in [BASE,SHA,'604','b54c6d46594575e9c46f3d2e46e8a282f657bfeca6f194a38060f3533684e72d','manager.UnrefUnit(u)','bus.close()','coverage_delta']:
            self.assertTrue(literal in refs,literal)
        for literal in ['ordinary-bootstrap196','systemctl','def actor(','def canonical_invalid(','namespace_failure_proof','pg516-terminal','pg517-terminal']:
            self.assertFalse(literal in java or literal in refs,literal)
        self.assertEqual(java.count('case "ordinary-api193"->"schubert-api";'),1)

    def test_literal_metadata_vectors_no_exclusion(self):
        # Numeric stat values and separate old file hash fixture, not Production generation.
        p=COVERAGE
        def node(md,sha=None):return {'metadata':md,'sha256':sha}
        old={p:node([1,42,0,0,0o40711,8,160,100,100]),p+'/parent':node([1,43,0,0,0o40700,2,60,50,50]),p+'/parent/old.exec':node([1,44,0,0,0o100600,1,17,55,55],'old-vector')}
        ids={'root-api193':[0,0],'root-web193':[0,0],'ordinary-api193':[991,976],'ordinary-web193':[990,975],'ordinary-inspector196':[993,978]}
        self.assertTrue(coverage_delta(copy.deepcopy(old),old,ids))
        actual=copy.deepcopy(old);actual[p]['metadata'][4]=0o40755;actual[p]['metadata'][8]=101
        self.assertTrue(coverage_delta(actual,old,ids))
        for index,(name,identity)in enumerate(ids.items()):
            actual[p+'/'+name]=node([1,100+index,*identity,0o40700,2,40,102,102]);actual[p]['metadata'][5]+=1;actual[p]['metadata'][6]+=20;actual[p]['metadata'][7:]=[102,102]
            self.assertTrue(coverage_delta(actual,old,ids))
        for key,value in [('mode',0o40777),('ino',90),('uid',1),('links',8)]:
            bad=copy.deepcopy(actual);bad[p]['metadata'][{'mode':4,'ino':1,'uid':2,'links':5}[key]]=value;self.assertFalse(coverage_delta(bad,old,ids))
        bad=copy.deepcopy(actual);bad[p+'/parent/old.exec']['sha256']='changed';self.assertFalse(coverage_delta(bad,old,ids))
        bad=copy.deepcopy(actual);bad[p+'/ordinary-bootstrap196']=node([1,200,991,976,0o40700,2,40,102,102]);self.assertFalse(coverage_delta(bad,old,ids))
        for index,value in [(2,0),(3,0),(4,0o40755),(5,3)]:
            bad=copy.deepcopy(actual);bad[p+'/ordinary-api193']['metadata'][index]=value;self.assertFalse(coverage_delta(bad,old,ids))
        self.assertFalse(coverage_delta(None,old,ids));self.assertFalse(coverage_delta(actual,None,ids));self.assertFalse(coverage_delta(actual,old,{}))


if __name__=='__main__':unittest.main()
