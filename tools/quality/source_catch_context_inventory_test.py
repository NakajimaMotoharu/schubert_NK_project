import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
JDK=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def facts(raw):
    result=[]
    for line in raw.splitlines():
        row=line.split('\t')
        if len(row)!=15 or row[0]!='CATCH' or row[8]not in {'true','false'}:raise ValueError('bounded resolved catch schema required')
        values=[int(row[n])for n in [4,5,6,7,9,10,11,12,13,14]]
        if min(values)<0 or values[0]<1 or values[1]<values[0] or values[3]<=values[2]:raise ValueError('valid catch extent/counts required')
        result.append(dict(zip(['kind','path','method','type','firstLine','lastLine','start','end','finalDirect','sameThrows','otherThrows','returns','assignments','breaks','continues'],row)))
    if not result:raise ValueError('nonempty catch facts required')
    return result


class CatchFacts(unittest.TestCase):
    def test_resolved_types_rethrow_mutation_nested_lambda_and_wrap_are_distinct(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-catch-facts-')as folder:
            base=pathlib.Path(folder);classes=base/'classes';classes.mkdir();source=base/'source';source.mkdir()
            fixture='''class Fixture {
void simple() throws Exception {try {throw new Exception();}catch(Exception e) {throw e;}}
void mutate() throws Exception {try {throw new Exception();}catch(Exception e) {e=new Exception();throw e;}}
void wrap() throws Exception {try {throw new Exception();}catch(Exception e) {throw new Exception(e);}}
void nested() throws Exception {try {throw new Exception();}catch(Exception e) {Runnable r=()->{if(true)return;throw new Error();};r.run();throw e;}}
void consume() {try {throw new IllegalArgumentException();}catch(RuntimeException e) {return;}}
void union() {try {throw new IllegalArgumentException();}catch(RuntimeException|Error e) {throw e;}}
}'''
            # Fixture is independent input, not generated from Production behavior.
            (source/'Fixture.java').write_text(fixture)
            compiled=subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(classes),str(ROOT/'tools/quality/SourceCatchContextInventory.java')],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,compiled.returncode,compiled.stderr)
            run=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourceCatchContextInventory',str(source),''],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,run.returncode,run.stderr)
            rows=facts(run.stdout);self.assertEqual(6,len(rows));by={r['method'].split('#')[1].split('(')[0]:r for r in rows}
            self.assertEqual('java.lang.Exception',by['simple']['type']);self.assertEqual('true',by['simple']['finalDirect']);self.assertEqual('1',by['simple']['sameThrows'])
            self.assertEqual('1',by['mutate']['assignments']);self.assertEqual('false',by['wrap']['finalDirect']);self.assertEqual('1',by['wrap']['otherThrows'])
            self.assertEqual('0',by['nested']['returns']);self.assertEqual('0',by['nested']['otherThrows']);self.assertEqual('1',by['nested']['sameThrows'])
            self.assertEqual('false',by['consume']['finalDirect']);self.assertEqual('1',by['consume']['returns'])
            self.assertEqual('true',by['union']['finalDirect'])
            self.assertEqual('java.lang.RuntimeException|java.lang.Error',by['union']['type'])
            for invalid in ['',run.stdout.replace('\ttrue\t','\tUNKNOWN\t',1),run.stdout.replace('\t1\t0\t','\t-1\t0\t',1)]:
                with self.assertRaises(ValueError):facts(invalid)


if __name__=='__main__':unittest.main()
