import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
JDK=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
FIELDS=('kind','path','method','type','firstLine','lastLine','catchStart','catchEnd','parameterStart','parameterEnd','bodyStart','bodyEnd','tryStart','tryEnd','pureSingleRethrow','exactUncheckedRoots','laterCatchOverlap','residualTryStable','proposedRemoval','catchIndex','catchTotal','eligibleInTry','hasResources','hasFinally')


def facts(raw):
    rows=[]
    for line in raw.splitlines():
        values=line.split('\t')
        if len(values)!=24 or values[0]!='PURE_RETHROW' or any(values[i]not in('true','false')for i in(14,15,16,17,18,22,23)):
            raise ValueError('exact nonempty typed pure-catch schema')
        row=dict(zip(FIELDS,values));numbers={k:int(row[k])for k in FIELDS[4:14]+FIELDS[19:22]}
        if not(1<=numbers['firstLine']<=numbers['lastLine'] and 0<=numbers['tryStart']<=numbers['catchStart']<=numbers['parameterStart']<numbers['parameterEnd']<=numbers['bodyStart']<numbers['bodyEnd']==numbers['catchEnd']<=numbers['tryEnd'] and 0<=numbers['catchIndex']<numbers['catchTotal'] and 0<=numbers['eligibleInTry']<=numbers['catchTotal']):
            raise ValueError('bounded one actual catch identity and UTF16 extents')
        if row['proposedRemoval']=='true' and not(row['pureSingleRethrow']==row['exactUncheckedRoots']==row['residualTryStable']=='true' and row['laterCatchOverlap']=='false'):
            raise ValueError('a proposal cannot bypass syntax/type/residual invariants')
        rows.append(row)
    if not rows:raise ValueError('nonempty resolved catch input')
    return rows


class PureCatchTypeFactsTest(unittest.TestCase):
    def test_only_exact_parameter_rethrow_without_later_capture_or_bare_try_is_proposed(self):
        fixture='''import java.io.IOException;
class Fixture {
static void unchecked() {} static void io() throws IOException {} static void cleanup() {}
static final Error other=new AssertionError();
static final class Resource implements AutoCloseable {public void close() throws IOException {}}
void finallyOnly(){try{unchecked();}catch(RuntimeException|Error e){throw e;}finally{cleanup();}}
void resourceOnly()throws IOException{try(var r=new Resource()){unchecked();}catch(RuntimeException|Error e){throw e;}}
void retainedOther(){try{io();}catch(RuntimeException e){throw e;}catch(IOException e){throw new IllegalStateException(e);}}
void broad(){try{io();}catch(RuntimeException|Error e){throw e;}catch(Exception e){throw new IllegalStateException(e);}}
void bare(){try{unchecked();}catch(RuntimeException e){throw e;}}
void twoDisjoint(){try{unchecked();}catch(RuntimeException e){throw e;}catch(Error e){throw e;}}
void extra(){try{unchecked();}catch(RuntimeException e){cleanup();throw e;}finally{cleanup();}}
void wrap(){try{unchecked();}catch(RuntimeException e){throw new IllegalStateException(e);}finally{cleanup();}}
void alias(){try{unchecked();}catch(RuntimeException e){throw other;}finally{cleanup();}}
void checked()throws IOException{try{io();}catch(Exception e){throw e;}}
void paren(){try{unchecked();}catch(RuntimeException e){throw(e);}finally{cleanup();}}
void nestedLambda(){try{unchecked();}catch(RuntimeException e){Runnable r=()->{throw new AssertionError();};r.run();throw e;}finally{cleanup();}}
}'''
        with tempfile.TemporaryDirectory(prefix='pgpt-pure-catch-')as folder:
            base=pathlib.Path(folder);classes=base/'classes';classes.mkdir();source=base/'source';source.mkdir();(source/'Fixture.java').write_text(fixture)
            compiled=subprocess.run([str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(ROOT/'tools/quality/SourcePureRethrowInventory.java')],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,compiled.returncode,compiled.stderr)
            result=subprocess.run([str(JDK/'java'),'-cp',str(classes),'SourcePureRethrowInventory',str(source),''],capture_output=True,text=True,timeout=30)
            self.assertEqual(0,result.returncode,result.stderr);rows=facts(result.stdout)
            named=lambda row:row['method'].split('#',1)[1].split('(',1)[0]
            self.assertEqual({'finallyOnly','resourceOnly','retainedOther'},{named(row)for row in rows if row['proposedRemoval']=='true'})
            first=next(r for r in rows if named(r)=='broad'and r['pureSingleRethrow']=='true');self.assertEqual('true',first['laterCatchOverlap'])
            self.assertTrue(all(r['residualTryStable']=='false'for r in rows if named(r)=='twoDisjoint'))
            self.assertEqual('false',next(r for r in rows if named(r)=='extra')['pureSingleRethrow'])
            self.assertEqual('false',next(r for r in rows if named(r)=='checked')['exactUncheckedRoots'])
            for bad in ('',result.stdout.replace('\ttrue\t','\tINVALID\t',1),result.stdout.replace('PURE_RETHROW','WRONG',1)):
                with self.assertRaises(ValueError):facts(bad)


if __name__=='__main__':unittest.main()
