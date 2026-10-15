import copy
import unittest
import pg3748_hygiene_signed_candidate as c


class Signed(unittest.TestCase):
    def fixture(self):
        modules={m:dict(zip(['tests','suites','mainClasses'],v))for m,v in c.whole.EXPECTED.items()};images={m:{'fixture/Class'+str(i)+'.class':'a'*64 for i in range(v['mainClasses'])}for m,v in modules.items()};images['api']['fixture/Class0.class']='b'*64
        return {'actualExit':0,'result':{'actualExit':0,'productionSource':c.SOURCE,'tests':3714,'suites':545,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'allOriginalCaseIdentitiesRetained':True,'oldNativeImported':False,'candidateNativePending':True,'F03Accepted':False,'formalAccepted':False,'global100':False,'newCases':[list(x)for x in c.whole.NEW_CASES],'modules':modules,'jarHashes':{m:'c'*64 for m in modules},'allPhysicalMainSha256':images,'changedClasses':[{'module':'api','class':'fixture/Class0.class','sourcePath':'src/schubert-nk-api/src/main/java/fixture/Class0.java','oldSha256':'a'*64,'newSha256':'b'*64}]}}

    def test_genuine_3714_all1643_and_exact_delta_never_old_native_or_quality_pass(self):
        good=self.fixture();g=c.validate_gate(good,c.SOURCE);before=copy.deepcopy(g['allPhysicalMainSha256']);before['api']['fixture/Class0.class']='a'*64
        try:
            c.GATE=g;self.assertEqual(1643,c.verify_delta(before,g['allPhysicalMainSha256']))
            wrong=copy.deepcopy(before);wrong['batch']['fixture/Class0.class']='d'*64
            with self.assertRaises(ValueError):c.verify_delta(wrong,g['allPhysicalMainSha256'])
            for key,value in [('tests',3712),('suites',543),('mainClasses',1642),('productionSource',c.OLD_SOURCE),('FESFlakyNotRun',1),('staticSixModules',1),('oldNativeImported',True),('formalAccepted',True),('F03Accepted',True),('global100',True),('changedClasses',[]),('allOriginalCaseIdentitiesRetained',False),('newCases',[])]:
                bad=copy.deepcopy(good);bad['result'][key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):c.validate_gate(bad,c.SOURCE)
            for bad in [None,{}, {'actualExit':False}, {'actualExit':1}]:
                with self.assertRaises(ValueError):c.validate_gate(bad,c.SOURCE)
        finally:c.GATE=None

    def test_host_template_is_new_only_and_contains_no_vm_operation(self):
        raw=c.main_source();compile(raw,'<fixed host-only release>','exec')
        for s in ['PG3748','PG3420','3714','545','pg3738-hygiene-whole-qualified-v1','qualification_matches(outer)',"len(gate['changedClasses'])"]:self.assertIn(s,raw)
        for s in ['systemctl','daemon-reload','server.info','Root/noargs']:self.assertNotIn(s,raw)


if __name__=='__main__':unittest.main()
