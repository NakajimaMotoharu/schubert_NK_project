"""Compiler coordinates/type and independent Java reference-language contract, not Production PT."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
JDK=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
FIELDS=['kind','path','firstLine','firstColumn','lastLine','lastColumn','leftType','rightType','operator','leftExpression','rightExpression','method']


def facts(raw):
    result=[]
    for line in raw.splitlines():
        values=line.split('\t')
        if len(values)!=12 or values[0]!='REFERENCE_IDENTITY'or values[8]not in('EQUAL_TO','NOT_EQUAL_TO'):raise ValueError('exact reference identity compiler row')
        a,b,c,d=map(int,values[2:6])
        if min(a,b,c,d)<1 or c<a or c==a and d<b:raise ValueError('bounded compiler coordinates')
        result.append(dict(zip(FIELDS,values)))
    return result


FIXTURE='''class Fixture {
 enum E {A,B}
 boolean objects(Object a,Object b){return a==b;}
 boolean arrays(byte[] a,byte[] b){return a!=b;}
 boolean current(Thread t){return Thread.currentThread()==t;}
 boolean primitive(int a,int b){return a==b;}
 boolean nil(Object a){return a==null;}
 boolean enumeration(E a,E b){return a==b;}
 void union(Throwable primary){try{if(System.nanoTime()==0)throw new IllegalStateException();throw new AssertionError();}catch(RuntimeException | Error closing){if(closing==primary){}if(primary==closing.getCause()){}}}
 record Value(int n) {}
 public static void main(String[] args) {
   var a=new Value(7); var b=new Value(7);
   if(!a.equals(b)||a==b)throw new AssertionError("equal values are distinct handles");
   class AlwaysEqual extends Throwable {
     @Override public boolean equals(Object other){return true;}
     @Override public int hashCode(){return 1;}
   }
   Throwable primary=new AlwaysEqual(), closing=new AlwaysEqual();
   if(!primary.equals(closing)||primary==closing)throw new AssertionError();
   primary.addSuppressed(closing);
   if(primary.getSuppressed().length!=1||primary.getSuppressed()[0]!=closing)throw new AssertionError();
   try{primary.addSuppressed(primary);throw new AssertionError();}catch(IllegalArgumentException expected){}
   System.out.println("REFERENCE_IDENTITY_NOT_VALUE_EQUALITY_OK");
 }
}'''


class ReferenceFacts(unittest.TestCase):
    def test_exact_reference_types_and_independent_language_contract(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-reference-facts-')as folder:
            base=pathlib.Path(folder);source=base/'source';source.mkdir();classes=base/'classes';classes.mkdir()
            (source/'Fixture.java').write_text(FIXTURE)
            r=subprocess.run([str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(ROOT/'tools/quality/SourceReferenceIdentityInventory.java')],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,r.returncode,r.stderr)
            r=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceReferenceIdentityInventory',str(source),''],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,r.returncode,r.stderr);rows=facts(r.stdout)
            self.assertEqual({'objects','arrays','current','union','main'},{r['method']for r in rows})
            self.assertEqual(2,len([r for r in rows if r['method']=='union']))
            one=[r for r in rows if r['method']=='objects'];self.assertEqual(1,len(one));self.assertEqual(('3','44','3','47'),tuple(one[0][k]for k in FIELDS[2:6]))
            self.assertEqual('java.lang.Object',one[0]['leftType'])
            self.assertEqual('byte[]',next(r for r in rows if r['method']=='arrays')['rightType'])
            r=subprocess.run([str(JDK/'javac'),'-d',str(classes),str(source/'Fixture.java')],capture_output=True,text=True,timeout=30);self.assertEqual(0,r.returncode,r.stderr)
            r=subprocess.run([str(JDK/'java'),'-cp',str(classes),'Fixture'],capture_output=True,text=True,timeout=30);self.assertEqual(0,r.returncode,r.stderr);self.assertEqual('REFERENCE_IDENTITY_NOT_VALUE_EQUALITY_OK\n',r.stdout)

    def test_unknown_shape_operator_and_invalid_coordinates_rejected(self):
        for raw in('x','REFERENCE_IDENTITY\tf\t0\t1\t1\t1\tA\tB\tEQUAL_TO\ta\tb\tm','REFERENCE_IDENTITY\tf\t1\t1\t1\t1\tA\tB\tPLUS\ta\tb\tm'):
            with self.assertRaises(ValueError):facts(raw)


if __name__=='__main__':unittest.main()
