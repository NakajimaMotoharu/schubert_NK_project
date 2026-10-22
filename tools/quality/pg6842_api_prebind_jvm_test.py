import hashlib
import json
import re
import subprocess
import unittest
import zipfile
import pg6842_api_prebind_original_jvm as p


class ApiPreBindDefinitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Definition canary uses the already qualified original30 Jar only; main will use original4203.
        qp=p.BASE/'PG6826-api-management-result-original-v1/manifest.json';pp=p.W/'pg6826-api-management-result-original-v1/manifest.safe.json'
        if p.sha(qp)!='8098c42d9af5490123b9a60fcfcb7a79c8f9f432862a34864078a4cb11e16f59':raise ValueError('qualified current30 first')
        q=json.loads(qp.read_bytes());private=json.loads(pp.read_bytes())
        if p.sha(pp)!=q['privateManifestSha256']:raise ValueError('all original30 physical map')
        jar=p.W/'pg6824-api-management-result-selected-v1/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
        with zipfile.ZipFile(jar)as z:
            actual={'api:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
        if actual!={k:v for k,v in private['allPhysicalMainSha256'].items()if k.startswith('api:')}:raise ValueError('all original API30 bytes')
        cls.raw=subprocess.check_output([str(p.TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',p.NAME],text=True)

    def test_original_api_order_and_late_empty_variant(self):
        value=p.inspect_order(self.raw);self.assertLess(value['optionalEmptyBci'],value['bindBci'])
        d=p.definitions();opened=d['block'](self.raw,p.OPEN)
        changed=re.sub(r'(^\s+)\d+(: invokestatic[^\n]*java/util/Optional.empty:)',r'\g<1>9999\2',opened,flags=re.M)
        self.assertNotEqual(opened,changed)
        with self.assertRaises(ValueError):p.inspect_order(self.raw.replace(opened,changed,1))

    def test_wrong_member_and_post_factory_allocation_rejected(self):
        d=p.definitions();ctor=d['block'](self.raw,p.CTOR)
        with self.assertRaises(ValueError):d['block'](self.raw.replace(' open(',' renamedOpen('),p.OPEN)
        changed=ctor.replace('    Code:\n','    Code:\n      9999: new #1 // class java/lang/Object\n',1)
        self.assertNotEqual(ctor,changed)
        with self.assertRaises(ValueError):p.inspect_order(self.raw.replace(ctor,changed,1))


if __name__=='__main__':unittest.main()
