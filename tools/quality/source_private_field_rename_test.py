"""Independent expected source tokens; negative candidates cannot hide behind alpha normalization."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from source_import_expansion_test import JDK,ROOT


class PrivateRename(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory(prefix='pgpt-private-rename-');cls.base=Path(cls.temporary.name);cls.classes=cls.base/'classes';cls.classes.mkdir()
        subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(cls.classes),str(ROOT/'tools/quality/SourcePrivateFieldRename.java'),str(ROOT/'tools/quality/IsolatedSourceOutput.java')],capture_output=True,check=True,timeout=30)

    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()

    def run_tool(self,action,source,request,output):
        return subprocess.run([str(JDK/'java'),'-cp',str(self.classes),'SourcePrivateFieldRename',action,str(source),'',str(request),str(output)],capture_output=True,text=True,timeout=30)

    def fixture(self,name,raw,owner='fixture.Subject',field='value',token='value='):
        base=self.base/name;base.mkdir();source=base/'source';source.mkdir();(source/'Subject.java').write_text(raw)
        offset=raw.index(token)
        request=base/'request.tsv';request.write_text('Subject.java\t'+owner+'\t'+field+'\t'+str(offset)+'\n')
        return source,request,base/'candidate'

    def test_exact_field_not_method_shadow_parameter_nested_or_literal(self):
        raw='''package fixture;
class Subject {
 private final int value;
 Subject(int value){this.value=value;}
 int value(){return value;}
 String label(){return "value";}
 java.util.function.IntSupplier supplier(){return ()->this.value;}
 class Nested {private int value=9; int read(){return value+Subject.this.value;}}
}
'''
        source,request,output=self.fixture('positive',raw,token='value;');result=self.run_tool('propose',source,request,output);self.assertEqual(0,result.returncode,result.stderr)
        expected=raw.replace('private final int value;','private final int retainedValue;').replace('this.value=value','this.retainedValue=value').replace('int value(){return value;}','int value(){return retainedValue;}').replace('()->this.value','()->this.retainedValue').replace('Subject.this.value','Subject.this.retainedValue')
        self.assertEqual(expected,(output/'Subject.java').read_text());self.assertEqual(raw,(source/'Subject.java').read_text());self.assertTrue(result.stdout.rstrip().endswith('FIELDS\t1'))
        verified=self.run_tool('verify',source,request,output);self.assertEqual(0,verified.returncode,verified.stderr)
        for mutation in [expected.replace('return "value"','return "retainedValue"'),expected.replace('return retainedValue','return 99'),expected.replace('Subject(int value){this.retainedValue=value;}','Subject(int other){this.retainedValue=other;}'),expected.replace('int value()','int renamed()'),raw]:
            (output/'Subject.java').write_text(mutation);bad=self.run_tool('verify',source,request,output);self.assertNotEqual(0,bad.returncode)
        (output/'Subject.java').write_text(expected)
        repeated=self.run_tool('propose',source,request,output);self.assertNotEqual(0,repeated.returncode);self.assertEqual(expected,(output/'Subject.java').read_text())

    def test_public_record_serialized_foreign_and_wrong_token_are_refused(self):
        cases=[('public','package fixture; class Subject {public int value=1;}', 'fixture.Subject','value='),
               ('record','package fixture; record Subject(int value) {}','fixture.Subject','value'),
               ('serialized','package fixture; class Subject implements java.io.Serializable {private static final long serialVersionUID=1L; private int value=1;}','fixture.Subject','value='),
               ('foreign','package fixture; class Subject {private int value=1;}','fixture.Foreign','value=')]
        for name,raw,owner,token in cases:
            source,request,output=self.fixture(name,raw,owner=owner,token=token);r=self.run_tool('propose',source,request,output);self.assertNotEqual(0,r.returncode);self.assertFalse(output.exists());self.assertEqual(raw,(source/'Subject.java').read_text())
        raw='package fixture; class Subject {private int value=1; String value(){return "value";}}'
        source,request,output=self.fixture('wrong-position',raw);request.write_text('Subject.java\tfixture.Subject\tvalue\t'+str(raw.index('"value"')+1)+'\n');self.assertNotEqual(0,self.run_tool('propose',source,request,output).returncode);self.assertFalse(output.exists())

    def test_static_array_null_and_existing_name_collision(self):
        raw='''package fixture;
class Subject {private static final int VALUE=3; private byte[] value=null;
 int value(int retainedValue){return VALUE+(value==null?retainedValue:value.length);}}
'''
        source,request,output=self.fixture('collision',raw,token='value=null');request.write_text(request.read_text()+'Subject.java\tfixture.Subject\tVALUE\t'+str(raw.index('VALUE=3'))+'\n')
        r=self.run_tool('propose',source,request,output);self.assertEqual(0,r.returncode,r.stderr)
        candidate=(output/'Subject.java').read_text();self.assertIn('byte[] retainedValueState=null',candidate);self.assertIn('int RETAINED_VALUE=3',candidate);self.assertIn('int value(int retainedValue)',candidate);self.assertIn('RETAINED_VALUE+(retainedValueState==null?retainedValue:retainedValueState.length)',candidate)

    def test_ancestor_symlink_cannot_place_candidate_inside_original(self):
        raw='package fixture; class Subject {private int value=1; int value(){return value;}}'
        source,request,_=self.fixture('alias-output',raw);alias=source.parent/'alias';alias.symlink_to(source,target_is_directory=True)
        result=self.run_tool('propose',source,request,alias/'generated')
        self.assertNotEqual(0,result.returncode)
        self.assertFalse((source/'generated').exists())
        self.assertEqual(['Subject.java'],sorted(str(p.relative_to(source))for p in source.rglob('*.java')))

    def test_unmentioned_inherited_public_member_name_is_not_hidden(self):
        raw='package fixture; class Subject extends Parent {private int value=1; int value(){return value;}}'
        source,request,output=self.fixture('inherited',raw)
        (source/'Parent.java').write_text('package fixture; class Parent {public int retainedValue=17;}')
        result=self.run_tool('propose',source,request,output);self.assertEqual(0,result.returncode,result.stderr)
        self.assertIn('private int retainedValueState=1',(output/'Subject.java').read_text())
        self.assertEqual('package fixture; class Parent {public int retainedValue=17;}',(output/'Parent.java').read_text())


if __name__=='__main__':unittest.main()
