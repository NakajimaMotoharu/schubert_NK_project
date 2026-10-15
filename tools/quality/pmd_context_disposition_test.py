"""Independent positive/managed/unknown/foreign-source rule-context boundaries."""
import copy
import unittest
from pmd_context_disposition import standalone_thread_context


class Context(unittest.TestCase):
    def test_only_exact_proven_standalone_scope_can_be_disposed(self):
        path='src/schubert-nk-api/src/main/java/Fixture.java'
        row={'rule':'DoNotUseThreads','path':path,'sourceSha256':'independent-fixed-source'}
        context={'sourceSha256':{path:'independent-fixed-source'},'approvedDirectJavaProcess':True,'externalJavaEEManaged':False,'noManagedDeploymentDescriptors':True,'ruleExplicitlyJ2EE':True,'moduleRoles':{'schubert-nk-api':'STANDALONE_JAVA_SERVICE'}}
        actual=standalone_thread_context(row,context);self.assertEqual('CONTEXT_NOT_APPLICABLE_J2EE_RULE',actual['disposition']);self.assertFalse(actual['qualityGatePass'])
        for key,value in [('approvedDirectJavaProcess',False),('externalJavaEEManaged',True),('externalJavaEEManaged',None),('noManagedDeploymentDescriptors',False),('ruleExplicitlyJ2EE',False),('moduleRoles',{})]:
            bad=copy.deepcopy(context);bad[key]=value;self.assertIsNone(standalone_thread_context(row,bad))
        bad=copy.deepcopy(context);bad['sourceSha256'][path]='foreign'
        with self.assertRaises(ValueError):standalone_thread_context(row,bad)
        other=dict(row,rule='CloseResource');self.assertIsNone(standalone_thread_context(other,context))


if __name__=='__main__':unittest.main()
