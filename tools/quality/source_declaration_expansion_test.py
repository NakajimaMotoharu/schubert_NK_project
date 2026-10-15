"""Independent literal initializer/array/annotation/order/text-block contracts."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from source_import_expansion_test import JDK,ROOT,parse


class Declarations(unittest.TestCase):
    def test_separate_variables_and_escaped_tab_retain_actual_compiler_semantics(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-declaration-contract-')as temporary:
            base=Path(temporary);original=base/'original';original.mkdir();candidate=base/'candidate';classes=base/'classes';classes.mkdir()
            source='''package fixture;
import java.lang.annotation.*;
@Target({ElementType.FIELD,ElementType.TYPE_USE}) @interface Mark {}
class Subject {
 @Mark private final int first=2, second=first+3;
 static String vector="""
     a\tb\tc
     """;
 int calculate(){int a[]=new int[]{first}, b=second; for(int i=0,j=1;i<j;i++){b+=a[i];} return b;}
}
'''
            (original/'Subject.java').write_text(source)
            tools=[ROOT/'tools/quality/SourceImportExpansion.java',ROOT/'tools/quality/SourceDeclarationExpansion.java',ROOT/'tools/quality/IsolatedSourceOutput.java']
            subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(classes),*map(str,tools)],capture_output=True,check=True,timeout=30)
            def probe(root):
                p=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceImportExpansion',str(root),''],capture_output=True,text=True,timeout=30)
                self.assertEqual(0,p.returncode,p.stderr);return parse(p.stdout)['Subject.java']
            before=probe(original)
            result=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceDeclarationExpansion',str(original),str(candidate)],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,result.returncode,result.stderr)
            value=(candidate/'Subject.java').read_text();self.assertNotIn('\t',value);self.assertIn('a\\tb\\tc',value)
            self.assertIn('first + 3',value);self.assertIn('int[] a',value);self.assertIn('int b',value)
            self.assertIn('for(int i=0,j=1',value)
            after=probe(candidate);self.assertEqual(before['binding'],after['binding']);self.assertEqual(before['declarations'],after['declarations'])
            fields=result.stdout.strip().split('\t');self.assertEqual(['2','4','2','1'],fields[-4:])
            self.assertEqual(source,(original/'Subject.java').read_text())
            repeated=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceDeclarationExpansion',str(original),str(candidate)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(0,repeated.returncode);self.assertEqual(value,(candidate/'Subject.java').read_text())
            alias=base/'alias';alias.symlink_to(original,target_is_directory=True)
            refused=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceDeclarationExpansion',str(original),str(alias/'generated')],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(0,refused.returncode);self.assertFalse((original/'generated').exists());self.assertEqual(source,(original/'Subject.java').read_text())


if __name__=='__main__':unittest.main()
