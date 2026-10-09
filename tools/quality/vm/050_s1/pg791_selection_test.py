"""Independent source/duplicate/missing XML and failing/skipped vectors."""
from pathlib import Path
import tempfile
import unittest
from pg791_completion_selected import source_names,xml_join


class Test(unittest.TestCase):
    def test_source_and_actual_xml_join(self):
        self.assertTrue(source_names(['Literal'],[Path('/fixed/Literal.java')]))
        for names,files in [(['Literal','Literal'],[Path('/fixed/Literal.java')]),(['Missing'],[Path('/fixed/Literal.java')]),(['Literal'],[Path('/a/Literal.java'),Path('/b/Literal.java')])]:self.assertFalse(source_names(names,files))
        with tempfile.TemporaryDirectory(prefix='pg791-xml-')as directory:
            p=Path(directory)/'one.xml';raw='<testsuite name="literal.Literal" tests="2" failures="0" errors="0" skipped="0"/>';p.write_text(raw)
            self.assertEqual((True,2),xml_join(['Literal'],[p]));self.assertFalse(xml_join(['Literal','Missing'],[p])[0]);self.assertFalse(xml_join(['Literal'],[p,p])[0]);self.assertFalse(xml_join([], [p])[0])
            for attribute in ('failures','errors','skipped'):
                p.write_text(raw.replace(attribute+'="0"',attribute+'="1"'));self.assertEqual((False,0),xml_join(['Literal'],[p]))
            p.write_text(raw.replace('tests="2"','tests="0"'));self.assertEqual((False,0),xml_join(['Literal'],[p]))


if __name__=='__main__':unittest.main()
