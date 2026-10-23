"""Metadata-only exact harness delta and independent quality/dependency mutation guards."""
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from inbox_protocol_harness_contract import verify_harness

ROOT=Path(__file__).resolve().parents[3]
PATH='tools/quality/harnesses/monitoring-api-jobs-pom.xml'
QUALIFIED="/home/mini/codex/project1/work/pgpt-runs/PG379/pg7614-dlq-health-six-compile-v1/snapshot/src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar"

class HarnessContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=subprocess.check_output(['git','show','a605c7287:'+PATH],cwd=ROOT)
        cls.after=(ROOT/PATH).read_bytes()

    def test_exact_one_binding_keeps_all_existing_quality(self):
        result=verify_harness(self.before,self.after,QUALIFIED)
        self.assertTrue(result['qualitySemanticsUnchanged'])
        self.assertFalse(result['productionPomChanged'])
        self.assertFalse(result['m2Overwritten'])

    def test_all_dependency_and_quality_mutations_are_rejected(self):
        for kind in ('version','scope','property-name','stale-path','exclusion','coverage','skip-tests','werror'):
            with self.subTest(kind=kind):
                root=ET.fromstring(self.after);ns=root.tag.partition('}')[0]+'}'
                node=next(n for n in root.find('{*}dependencies') if n.findtext('{*}artifactId')=='schubert-nk-protocol')
                if kind=='version':node.find('{*}version').text='unknown'
                elif kind=='scope':node.find('{*}scope').text='compile'
                elif kind=='property-name':node.find('{*}systemPath').text='${unknown.protocol}'
                elif kind=='stale-path':root.find('{*}properties')[0].text='/stale/m2/protocol.jar'
                elif kind=='exclusion':ET.SubElement(node,ns+'exclusions')
                elif kind=='coverage':root.find('.//{*}minimum').text='0.99'
                else:
                    plugins=root.find('{*}build/{*}plugins')
                    name='maven-surefire-plugin' if kind=='skip-tests' else 'maven-compiler-plugin'
                    plugin=next(p for p in plugins if p.findtext('{*}artifactId')==name)
                    config=plugin.find('{*}configuration')
                    if kind=='skip-tests':ET.SubElement(config,ns+'skipTests').text='true'
                    else:
                        args=config.find('{*}compilerArgs');args.remove(next(n for n in args if n.text=='-Werror'))
                with self.assertRaises(ValueError):verify_harness(self.before,ET.tostring(root),QUALIFIED)

if __name__=='__main__':unittest.main()
