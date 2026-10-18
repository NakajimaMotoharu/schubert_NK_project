"""Independent tiny XML counter oracle; text hints cannot close branch or trace acceptance."""
import unittest
from pyflakes.api import checkPath
import pg5118_batch_residual_map as target

COUNT='<counter type="LINE" missed="2" covered="0"/><counter type="METHOD" missed="1" covered="0"/><counter type="CLASS" missed="1" covered="0"/><counter type="BRANCH" missed="2" covered="0"/>'
METHOD='<method name="run" desc="()V" line="10">'+COUNT+'</method>'
CLASS='<class name="dev/example/A" sourcefilename="A.java">'+METHOD+COUNT+'</class>'
LINES='<sourcefile name="A.java"><line nr="10" mi="3" ci="0" mb="2" cb="0"/><line nr="11" mi="1" ci="0" mb="0" cb="0"/><counter type="LINE" missed="2" covered="0"/></sourcefile>'
XML=('<report name="literal"><package name="dev/example">'+CLASS+LINES+'</package>'+COUNT+'</report>').encode()


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
        raw=XML.replace(b'missed="2" covered="0"',b'missed="0" covered="2"').replace(b'missed="1" covered="0"',b'missed="0" covered="1"').replace(b'mi="3" ci="0"',b'mi="0" ci="3"').replace(b'mi="1" ci="0"',b'mi="0" ci="1"')
        value=target.parse_report(raw)
        self.assertEqual([],value['classes'])
        self.assertEqual(0,value['affectedMethods'])
        for path in (target.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_two_classes_shared_source_line_is_one_covered_line(self):
        count='<counter type="LINE" missed="0" covered="1"/><counter type="METHOD" missed="0" covered="1"/><counter type="CLASS" missed="0" covered="1"/>'
        cls='<class name="dev/A" sourcefilename="A.java">'+count+'</class>'
        source='<sourcefile name="A.java"><line nr="10" mi="1" ci="3"/><counter type="LINE" missed="0" covered="1"/></sourcefile>'
        total='<counter type="LINE" missed="0" covered="1"/><counter type="METHOD" missed="0" covered="2"/><counter type="CLASS" missed="0" covered="2"/>'
        raw=('<report><package name="dev">'+cls+cls.replace('dev/A','dev/A$1')+source+'</package>'+total+'</report>').encode()
        value=target.parse_report(raw)
        self.assertEqual({'missed':0,'covered':1},value['lineReconciliation']['sourceUnique'])
        self.assertEqual({'missed':0,'covered':2},value['lineReconciliation']['classOccurrences'])
        self.assertEqual({'missed':0,'covered':1},value['lineReconciliation']['classOverlapDelta'])
        for bad in (raw.replace(b'ci="3"',b'ci="0"'),raw.replace(b'</sourcefile>',b'<line nr="10" mi="0" ci="1"/></sourcefile>')):
            with self.assertRaises(ValueError):target.parse_report(bad)

    def test_literal_sixfield_native_metadata_is_qualified_not_discarded(self):
        four={k:{'missed':v,'covered':0}for k,v in zip(target.COUNTERS,[2,1,1,2],strict=True)}
        native={**four,'classByteMismatch':0,'formal':False}
        self.assertEqual(four,target.measurement_counters(native))
        for change in ({'classByteMismatch':1},{'classByteMismatch':False},{'formal':True},{'unknown':0},{'LINE':{'missed':False,'covered':0}}):
            with self.subTest(change=change),self.assertRaises(ValueError):target.measurement_counters({**native,**change})
        del native['formal']
        with self.assertRaises(ValueError):target.measurement_counters(native)


if __name__=='__main__':unittest.main()
