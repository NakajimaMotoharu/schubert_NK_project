import copy
import unittest
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from pg6104_sourcefile_line_projection import sourcefile_lines,projection


class PhysicalLineDomainTest(unittest.TestCase):
    def fixture(self):
        # One class misses the line while another class executes that same physical line.
        tree=ET.fromstring('<report><package name="p"><class name="p/Outer" sourcefilename="Outer.java"><counter type="LINE" missed="1" covered="0"/></class><class name="p/Outer$Inner" sourcefilename="Outer.java"><counter type="LINE" missed="0" covered="1"/></class><sourcefile name="Outer.java"><line nr="10" mi="1" ci="2" mb="0" cb="0"/><counter type="LINE" missed="0" covered="1"/></sourcefile></package><counter type="LINE" missed="0" covered="1"/></report>')
        artifacts=[dict(path='src/schubert-nk-web/src/main/java/p/Outer.java',module='web',kind='JAVA',owner='owner')]
        return tree,artifacts

    def test_class_missed_line_is_retained_even_when_source_line_is_covered(self):
        tree,artifacts=self.fixture();rows,owners,total=sourcefile_lines(tree,'web',artifacts)
        self.assertEqual({'missed':0,'covered':1},total)
        self.assertEqual({'missed':1,'covered':1},rows[0]['classFamilyLine'])
        self.assertEqual({'owner':total},owners)

    def test_unknown_owner_duplicate_file_and_false_source_counter_fail(self):
        tree,artifacts=self.fixture()
        with self.assertRaises(ValueError):sourcefile_lines(tree,'web',[])
        tree.find('package').append(copy.deepcopy(tree.find('package/sourcefile')))
        with self.assertRaises(ValueError):sourcefile_lines(tree,'web',artifacts)

    def test_actual_original_source_and_class_domains_keep_all_eight_class_misses(self):
        root=Path(__file__).resolve().parents[2]
        base=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
        manifest=json.loads((base/'PG6102-current-host-measurement-v1/manifest.json').read_bytes())
        inventory=json.loads((root.parent/'pgpt-runs/PG379/pg6102-current-support-trace-v1/candidate-485_WBS網羅性・受入対応.json').read_bytes())
        result=projection(manifest,inventory['currentPhysicalCandidate']['artifacts'],root)
        self.assertEqual(3525,result['sourcefileLineTotals']['missed'])
        self.assertEqual(3533,result['classFamilyLineTotals']['missed'])
        differences=[r for r in result['domainDifferences']if r['classFamilyLine']['missed']!=r['sourcefileLine']['missed']]
        self.assertEqual(6,len(differences))
        self.assertEqual(8,sum(r['classFamilyLine']['missed']-r['sourcefileLine']['missed']for r in differences))
        self.assertTrue(result['noClassMissesRemoved'])
        tree,artifacts=self.fixture();tree.find('package/sourcefile/counter').set('missed','1')
        with self.assertRaises(ValueError):sourcefile_lines(tree,'web',artifacts)


if __name__=='__main__':unittest.main()
