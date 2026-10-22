import hashlib
import json
import subprocess
import unittest
import zipfile
import pg6876_web_prebind_current_jvm as p
from pg6820_web_prebind_original_jvm import OPEN,block


class OriginalGreenWebPrebindDefinitionTest(unittest.TestCase):
    def raw(self):
        public=p.BASE/'PG6854-web-deadline-original-v1/manifest.json'
        self.assertEqual('69dba2782be8034e9efac8505b5019d466da0100bd1a3bc105f57760b61466fd',p.sha(public))
        q=json.loads((p.W/'pg6854-web-deadline-original-v1/manifest.safe.json').read_bytes())
        jar=p.W/'pg6852-web-deadline-green-v1/source/src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
        with zipfile.ZipFile(jar)as z:
            actual={'web:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
        self.assertEqual({k:v for k,v in q['allPhysicalMainSha256'].items()if k.startswith('web:')},actual)
        return subprocess.check_output([str(p.TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',p.NAME],text=True)

    def test_actual_green_class_order_and_exact_member(self):
        raw=self.raw();x=p.inspect_order(raw)
        self.assertEqual([6,11,20,27],[x[k]for k in('diagnosticInitBci','optionalEmptyBci','bindBci','startBci')])
        self.assertIn(' open(',block(raw,OPEN).splitlines()[0])

    def test_wrong_member_and_late_empty_are_rejected(self):
        raw=self.raw()
        with self.assertRaises(ValueError):p.inspect_order(raw.replace(' open(',' unexpected('))
        with self.assertRaises(ValueError):p.inspect_order(raw.replace('11: invokestatic','99: invokestatic'))


if __name__=='__main__':unittest.main()
