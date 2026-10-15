"""Independent integer-value golden vectors, token noninterference, and real semantic canaries."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from source_import_expansion_test import JDK,ROOT


class Octal(unittest.TestCase):
    def test_all_widths_bases_literal_boundaries_and_semantic_negative(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-octal-')as temporary:
            base=Path(temporary);classes=base/'classes';classes.mkdir();source=base/'source';source.mkdir();output=base/'candidate'
            tools=['SourceOctalLiteralExpansion.java','IsolatedSourceOutput.java','SourceSemanticEquivalence.java','SourcePrivateFieldRename.java']
            c=subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(classes),*[str(ROOT/'tools/quality'/n)for n in tools]],capture_output=True,text=True,timeout=30);self.assertEqual(0,c.returncode,c.stderr)
            raw='''class Subject {
 int owner=0600, executable=0755, zero=00, low=-010, bits=037777777777;
 long wide=01777777777777777777777L, underscored=0_7_7_7l;
 int decimal=600, hex=0x180, binary=0b110000000, single=0;
 double floating=0600.0; String text="0600 0755"; char character='0'; //0600
 int value(){return owner;}
}'''
            expected=raw.replace('owner=0600','owner=0x180').replace('executable=0755','executable=0x1ed').replace('zero=00','zero=0x0').replace('low=-010','low=-0x8').replace('bits=037777777777','bits=0xffffffff').replace('wide=01777777777777777777777L','wide=0xffffffffffffffffL').replace('underscored=0_7_7_7l','underscored=0x1ffL')
            (source/'Subject.java').write_text(raw)
            def run(name,*args):return subprocess.run([str(JDK/'java'),'-cp',str(classes),name,*map(str,args)],capture_output=True,text=True,timeout=30)
            r=run('SourceOctalLiteralExpansion',source,output);self.assertEqual(0,r.returncode,r.stderr);self.assertEqual(expected,(output/'Subject.java').read_text());self.assertTrue(r.stdout.rstrip().endswith('OCTAL\t7'))
            proof=run('SourceSemanticEquivalence',source,output,'');self.assertEqual(0,proof.returncode,proof.stderr)
            for mutation in [expected.replace('owner=0x180','owner=0x181'),expected.replace('long wide','double wide'),expected.replace('"0600 0755"','"600 755"'),expected.replace('return owner','return single')]:
                (output/'Subject.java').write_text(mutation);self.assertNotEqual(0,run('SourceSemanticEquivalence',source,output,'').returncode)
            self.assertEqual(raw,(source/'Subject.java').read_text())
            alias=base/'alias';alias.symlink_to(source,target_is_directory=True);self.assertNotEqual(0,run('SourceOctalLiteralExpansion',source,alias/'inner').returncode);self.assertFalse((source/'inner').exists())
            self.assertNotEqual(0,run('SourceOctalLiteralExpansion',source,output).returncode)
            invalid=base/'invalid';invalid.mkdir();(invalid/'Subject.java').write_text('class Subject {int invalid=08;}');self.assertNotEqual(0,run('SourceOctalLiteralExpansion',invalid,base/'not-written').returncode);self.assertFalse((base/'not-written').exists())


if __name__=='__main__':unittest.main()
