"""Independent tiny XML counter oracle; text hints cannot close branch or trace acceptance."""
import unittest
from pyflakes.api import checkPath
import pg5118_batch_residual_map as target

COUNT='<counter type="LINE" missed="2" covered="0"/><counter type="METHOD" missed="1" covered="0"/><counter type="CLASS" missed="1" covered="0"/><counter type="BRANCH" missed="2" covered="0"/>'
METHOD='<method name="run" desc="()V" line="10">'+COUNT+'</method>'
CLASS='<class name="dev/example/A" sourcefilename="A.java">'+METHOD+COUNT+'</class>'
XML=('<report name="literal"><package name="dev/example">'+CLASS+'</package>'+COUNT+'</report>').encode()


class Residual(unittest.TestCase):
    def test_literal_counter_and_descriptor_not_guessed_branch_outcome(self):
        value=target.parse_report(XML)
        self.assertEqual((1,1,1),(value['affectedClasses'],value['affectedMethods'],value['physicalReportedCodeClasses']))
        self.assertEqual({'LINE':2,'METHOD':1,'CLASS':1,'BRANCH':2},{k:v['missed']for k,v in value['counters'].items()})
        method=value['classes'][0]['methods'][0]
        self.assertEqual(('run','()V',10),(method['name'],method['descriptor'],method['line']))
        self.assertEqual('UNKNOWN_REQUIRES_CODE_OR_BYTECODE_AND_INDEPENDENT_PT',method['branchOutcome'])

    def test_mismatch_duplicate_negative_and_unsafe_source_refuse(self):
        for raw in (XML.replace(b'</report>',b'<counter type="LINE" missed="2" covered="0"/></report>'),
                    XML.replace(b'missed="2"',b'missed="-1"',1),
                    XML.replace(b'A.java',b'../A.java'),XML.replace(b'dev/example/A',b'dev//A'),
                    XML.replace(b'</package>',CLASS.encode()+b'</package>'),
                    XML.replace(b'</class>',METHOD.encode()+b'</class>')):
            with self.subTest(raw=raw[:40]),self.assertRaises(ValueError):target.parse_report(raw)
        wrong=XML.rsplit(b'<counter type="LINE" missed="2" covered="0"/>',1)
        with self.assertRaisesRegex(ValueError,'reconcile'):
            target.parse_report(b'<counter type="LINE" missed="3" covered="0"/>'.join(wrong))

    def test_no_residual_is_only_counter_measurement_not_new_tests(self):
        raw=XML.replace(b'missed="2" covered="0"',b'missed="0" covered="2"').replace(b'missed="1" covered="0"',b'missed="0" covered="1"')
        value=target.parse_report(raw)
        self.assertEqual([],value['classes'])
        self.assertEqual(0,value['affectedMethods'])
        for path in (target.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
