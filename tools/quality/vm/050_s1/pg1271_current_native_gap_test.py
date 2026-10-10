import unittest
from pg1271_current_native_gap import coordinates


class CoordinatesTest(unittest.TestCase):
    def test_literal_counter_join_methods_and_boundary_lines(self):
        expected={k:{'missed':1,'covered':2}for k in ['LINE','METHOD','CLASS','BRANCH']}
        counters=''.join('<counter type="'+k+'" missed="1" covered="2"/>'for k in expected)
        raw=('<report><package name="literal"><class name="literal/Fixture" sourcefilename="Fixture.java"><method name="run" desc="()V" line="12"><counter type="BRANCH" missed="1" covered="1"/></method><counter type="LINE" missed="1" covered="2"/></class><sourcefile name="Fixture.java"><line nr="12" mi="1" ci="2" mb="1" cb="1"/><line nr="13" mi="0" ci="2" mb="0" cb="1"/></sourcefile></package>'+counters+'</report>').encode()
        result=coordinates(raw,expected);self.assertEqual(len(result),1);self.assertEqual(result[0]['methods'][0]['name'],'run');self.assertEqual([v['nr']for v in result[0]['sourceFileMissedLines']],[12])
        for changed in [raw.replace(b'<report>',b'<wrong>').replace(b'</report>',b'</wrong>'),raw.replace(b'missed="1"',b'missed="0"')]:
            with self.assertRaises(ValueError):coordinates(changed,expected)
        for value in [None,'raw']:
            with self.assertRaises(ValueError):coordinates(value,expected)


if __name__=='__main__':unittest.main()
