"""Compiler-derived risk facts distinguish private fields, public/record and serialized state."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from source_import_expansion_test import ROOT,JDK


def fields(text):
    result=[]
    for line in text.splitlines():
        p=line.split('\t')
        if len(p)!=15 or p[0]!='FIELD':raise ValueError('exact actual field schema')
        result.append({'path':p[1],'owner':p[2],'name':p[3],'modifiers':p[4],'record':p[5]=='true','serializable':p[6]=='true','ownerAnnotations':p[7],'fieldAnnotations':p[8],'declFirstLine':int(p[9]),'declLastLine':int(p[10]),'nameLine':int(p[11]),'nameStart':int(p[12]),'start':int(p[13]),'end':int(p[14])})
    return result


class FieldFacts(unittest.TestCase):
    def test_private_record_public_and_serialization_are_not_conflated(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-field-facts-')as d:
            root=Path(d);source=root/'src';source.mkdir();classes=root/'classes';classes.mkdir()
            raw='''package fixture;
class Plain {private final int value=1; public int value(){return value;} public int visible;}
class Serialized implements java.io.Serializable {private static final long serialVersionUID=1L; private int value=2; int value(){return value;}}
record RecordValue(int value) {public int value(){return value;}}
'''
            (source/'Fixture.java').write_text(raw)
            subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(classes),str(ROOT/'tools/quality/SourceFieldNamingInventory.java')],capture_output=True,check=True,timeout=30)
            r=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceFieldNamingInventory',str(source),''],capture_output=True,text=True,timeout=30);self.assertEqual(0,r.returncode,r.stderr)
            rows={(x['owner'],x['name']):x for x in fields(r.stdout)}
            plain=rows[('fixture.Plain','value')];self.assertIn('private',plain['modifiers']);self.assertFalse(plain['record']);self.assertFalse(plain['serializable']);self.assertEqual(2,plain['nameLine']);self.assertEqual('value',raw[plain['nameStart']:plain['nameStart']+5])
            self.assertIn('public',rows[('fixture.Plain','visible')]['modifiers']);self.assertTrue(rows[('fixture.Serialized','value')]['serializable']);self.assertTrue(rows[('fixture.RecordValue','value')]['record'])
            self.assertEqual(raw,(source/'Fixture.java').read_text())


if __name__=='__main__':unittest.main()
