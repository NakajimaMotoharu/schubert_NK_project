import unittest
from pmd_contract_disposition import classify_contract


class Contracts(unittest.TestCase):
    def test_current_source_context_and_contract_evidence_cannot_be_guessed(self):
        path='src/schubert-nk-web/src/main/java/example/Reader.java';row={'path':path,'sourceSha256':'a'*64,'rule':'UseProperClassLoader','coordinates':{'beginline':12}}
        c={'source':'b'*40,'sourceSha256':{path:'a'*64},'vendorExplicitJ2ee':{'UseProperClassLoader':True},'approvedDirectJavaProcess':True,'externalJavaEEManaged':False,'noManagedDeploymentDescriptors':True,'moduleRoles':{'schubert-nk-web':'STANDALONE_JAVA_SERVICE'},'architectureEvidence':['approved-main-doc-hash']}
        v=classify_contract(row,c,{});self.assertEqual('CONTEXT_NOT_APPLICABLE_J2EE_RULE',v['disposition']);self.assertFalse(v['qualityGatePass']);self.assertFalse(v['rawWarningRemoved'])
        for key,value in [('externalJavaEEManaged',True),('approvedDirectJavaProcess',False),('moduleRoles',{}),('vendorExplicitJ2ee',{})]:self.assertIsNone(classify_contract(row,{**c,key:value},{}))
        with self.assertRaises(ValueError):classify_contract({**row,'sourceSha256':'c'*64},c,{})
        self.assertIsNone(classify_contract({**row,'rule':'CloseResource'},c,{}))
        r={**row,'rule':'UnusedReturnValue'};p={'sourceSha256':row['sourceSha256'],'wholeSource':c['source'],'independentXmlQualified':True,'exactFindingLines':[12],'evidence':['actual-current-test-xml'],'disposition':'VALIDATING_PEEK_SIDE_EFFECT','basis':'Pinned STRICT reader consumes trailing input/throws; literal negative inputs fail without extra unreachable branch.'}
        self.assertEqual('VALIDATING_PEEK_SIDE_EFFECT',classify_contract(r,c,{('UnusedReturnValue',path):p})['disposition'])
        for key,value in [('wholeSource','other'),('independentXmlQualified',False),('evidence',[]),('exactFindingLines',[13])]:
            with self.assertRaises(ValueError):classify_contract(r,c,{('UnusedReturnValue',path):{**p,key:value}})


if __name__=='__main__':unittest.main()
