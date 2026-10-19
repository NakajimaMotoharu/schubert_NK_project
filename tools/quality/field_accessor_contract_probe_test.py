import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
JDK=ROOT.parent/'toolchain/jdk-25.0.4/bin'


class AccessorMetadata(unittest.TestCase):
    def test_actual_compile_only_dependencies_are_declared_and_not_silently_runtime(self):
        import pg5584_field_accessor_inspection as entry
        paths,metadata=entry.compile_only_artifacts()
        self.assertEqual(len(paths),2)
        self.assertEqual({r['version']for r in metadata},{'4.10.4','3.0.2'})
        self.assertTrue(all(r['scope']=='COMPILER_ONLY_NOT_RUNTIME'and len(r['sha256'])==64 for r in metadata))

    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='pg5584-accessor-pure-');cls.base=Path(cls.temp.name);cls.classes=cls.base/'classes';cls.classes.mkdir()
        result=subprocess.run([str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(cls.classes),
            *[str(ROOT/'tools/quality'/n)for n in('IsolatedSourceOutput.java','SourcePrivateFieldRename.java','FieldAccessorContractProbe.java')]],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def run_probe(self,name,raw,requests):
        directory=self.base/name;directory.mkdir();source=directory/'input';source.mkdir();(source/'Subject.java').write_text(raw)
        request=directory/'request.tsv';request.write_text(requests)
        result=subprocess.run([str(JDK/'java'),'-cp',str(self.classes),'FieldAccessorContractProbe',str(source),'',str(request)],capture_output=True,text=True,timeout=30)
        self.assertEqual((source/'Subject.java').read_text(),raw)
        return result

    def test_enum_throwable_and_nonserializable_are_reported_not_waived(self):
        raw='''package fixture;
enum Mode { A;
 private final int value=1;
 public int value(){return value;}
}
class Failure extends Exception {
 private static final long serialVersionUID=1L;
 private final int reason=1;
 public int reason(){return reason;}
}
class Ordinary {
 private final int count=1;
 public int count(){return count;}
}
'''
        result=self.run_probe('typed',raw,'Subject.java\t3\tvalue\nSubject.java\t8\treason\nSubject.java\t12\tcount\n')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('\tfixture.Mode\tENUM\ttrue\tfalse\ttrue',result.stdout)
        self.assertIn('\tfixture.Failure\tTHROWABLE\ttrue\ttrue\ttrue',result.stdout)
        self.assertIn('\tfixture.Ordinary\tNON_SERIALIZABLE_CLASS\tfalse\tfalse\ttrue',result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith('COUNT\t3'))

    def test_wrong_literal_getter_wrong_coordinate_and_missing_field_refuse(self):
        raw='package fixture; class Subject {private int value=1; public int value(){return 99;}}'
        result=self.run_probe('literal',raw,'Subject.java\t1\tvalue\n');self.assertNotEqual(result.returncode,0)
        raw='package fixture; class Subject {private int value=1; public int value(){return value;}}'
        for name,request in(('wrong','Subject.java\t2\tvalue\n'),('unknown','Subject.java\t1\tmissing\n')):
            self.assertNotEqual(self.run_probe(name,raw,request).returncode,0)

    def test_missing_symbol_diagnostic_stays_nonzero_and_does_not_create_class_files(self):
        source=self.base/'diagnostic';source.mkdir();(source/'Broken.java').write_text('class Broken {MissingType value;}')
        result=subprocess.run([str(JDK/'java'),'-cp',str(self.classes),'FieldAccessorContractProbe','--diagnose',str(source),''],capture_output=True,text=True,timeout=30)
        self.assertNotEqual(result.returncode,0);self.assertIn('DIAGNOSTIC_ERRORS\t1',result.stdout)
        self.assertIn('compiler.err.cant.resolve',result.stdout);self.assertFalse(list(source.glob('*.class')))


if __name__=='__main__':unittest.main()
