"""Independent Java identity/JDK-contract fixtures, never generated Production expected values."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
JDK=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def facts(raw):
    rows=[]
    for line in raw.splitlines():
        row=line.split('\t')
        if len(row)!=10 or row[0]!='SELF_SUPPRESSION_GUARD':raise ValueError('exact typed identity fact required')
        a,b,c,d=map(int,row[2:6])
        if min(a,b,c,d)<1 or c<a or c==a and d<b:raise ValueError('bounded exact coordinate required')
        rows.append(dict(zip(['kind','path','firstLine','firstColumn','lastLine','lastColumn','leftType','rightType','leftSymbol','rightSymbol'],row)))
    return rows


FIXTURE='''class Fixture {
void direct(Throwable a,Throwable b) {if(a!=b)a.addSuppressed(b);}
void reverse(RuntimeException a,Throwable b) {if(a!=b)b.addSuppressed(a);}
void conjunct(Throwable a,Throwable b,boolean ready) {if(ready && (a!=b))a.addSuppressed(b);}
void or(Throwable a,Throwable b,boolean ready) {if(ready || a!=b)a.addSuppressed(b);}
void equal(Throwable a,Throwable b) {if(a==b)a.addSuppressed(b);}
void wrong(Throwable a,Throwable b,Throwable c) {if(a!=b)a.addSuppressed(c);}
void mutate(Throwable a,Throwable b) {if(a!=b){b=a;a.addSuppressed(b);}}
void nested(Throwable a,Throwable b) {if(a!=b){Runnable r=()->a.addSuppressed(b);}}
void body(Throwable a,Throwable b) {if(true){if(a!=b){}a.addSuppressed(b);}}
Throwable field;
void mutableField(Throwable b) {if(field!=b)field.addSuppressed(b);}
void mutateCondition(Throwable a,Throwable b) {if(a!=b && (b=a)!=null)a.addSuppressed(b);}
public static void main(String[] args) {
 Throwable same=new Throwable();
 try {same.addSuppressed(same);throw new AssertionError("same identity must reject");}
 catch(IllegalArgumentException expected) {if(!"Self-suppression not permitted".equals(expected.getMessage()))throw new AssertionError();}
 class EqualThrowable extends Throwable {
  @Override public boolean equals(Object other) {return true;}
  @Override public int hashCode() {return 1;}
 }
 Throwable a=new EqualThrowable(),b=new EqualThrowable();
 if(a==b||!a.equals(b))throw new AssertionError();
 a.addSuppressed(b);
 if(a.getSuppressed().length!=1||a.getSuppressed()[0]!=b)throw new AssertionError();
 System.out.println("JDK_IDENTITY_CONTRACT_OK");
}
}'''


class IdentityFacts(unittest.TestCase):
    def test_exact_guards_and_jdk_self_suppression(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-identity-facts-')as folder:
            base=pathlib.Path(folder);classes=base/'classes';classes.mkdir();source=base/'source';source.mkdir()
            (source/'Fixture.java').write_text(FIXTURE)
            compiled=subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(classes),str(ROOT/'tools/quality/SourceSuppressionIdentityInventory.java')],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,compiled.returncode,compiled.stderr)
            run=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceSuppressionIdentityInventory',str(source),''],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,run.returncode,run.stderr)
            rows=facts(run.stdout)
            self.assertEqual(3,len(rows));self.assertEqual({'2','3','4'},{r['firstLine']for r in rows})
            self.assertEqual('java.lang.RuntimeException',rows[1]['leftType']);self.assertEqual('java.lang.Throwable',rows[1]['rightType'])
            build=subprocess.run([str(JDK/'javac'),'-d',str(classes),str(source/'Fixture.java')],capture_output=True,text=True,timeout=30);self.assertEqual(0,build.returncode,build.stderr)
            jdk=subprocess.run([str(JDK/'java'),'-cp',str(classes),'Fixture'],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,jdk.returncode,jdk.stderr);self.assertEqual('JDK_IDENTITY_CONTRACT_OK\n',jdk.stdout)
            for bad in ['UNKNOWN\tfile\t1\t1\t1\t1\tA\tB\ta\tb','SELF_SUPPRESSION_GUARD\tf\t0\t1\t1\t1\tA\tB\ta\tb']:
                with self.assertRaises(ValueError):facts(bad)


if __name__=='__main__':unittest.main()
