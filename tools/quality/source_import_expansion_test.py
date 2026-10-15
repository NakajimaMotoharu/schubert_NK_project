"""Independent compiler-binding fixtures; no Production source changed."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
JDK=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
TOOL=ROOT/'tools/quality/SourceImportExpansion.java'


def parse(text):
    result={};current=None
    for line in text.splitlines():
        parts=line.split('\t')
        if parts[0]=='FILE':
            current=parts[1]
            if current in result:raise ValueError('duplicate source')
            result[current]={'imports':[]}
        elif parts[0]=='BINDINGS':result[current]['binding']=parts[1]
        elif parts[0]=='DECLARATIONS':result[current]['declarations']=parts[1]
        elif parts[0]=='IMPORT':result[current]['imports'].append((int(parts[1]),int(parts[2]),parts[3]))
        else:raise ValueError('unknown probe output')
    return result


def replace_imports(raw,edits):
    # Compiler source positions are UTF-16 code units, not Python Unicode indices.
    value=raw.encode('utf-16-le');last=len(value)
    for start,end,replacement in sorted(edits,reverse=True):
        start*=2;end*=2
        if not(0<=start<end<=last):raise ValueError('overlapping or invalid edit')
        original=value[start:end].decode('utf-16-le')
        if not(original.startswith('import ')and original.endswith('.*;')):raise ValueError('only wildcard import spans permitted')
        value=value[:start]+replacement.encode('utf-16-le')+value[end:];last=start
    return value.decode('utf-16-le')


class Expansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='pgpt-import-probe-')
        cls.base=Path(cls.temp.name);cls.classes=cls.base/'classes';cls.classes.mkdir()
        subprocess.run([str(JDK/'javac'),'-Xlint:all','-Werror','-d',str(cls.classes),str(TOOL)],capture_output=True,check=True,timeout=30)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def probe(self,name,sources,allow_failure=False):
        root=self.base/name;root.mkdir()
        for path,raw in sources.items():(root/path).write_text(raw)
        command=[str(JDK/'java'),'-cp',str(self.classes),'SourceImportExpansion',str(root),'']
        result=subprocess.run(command,capture_output=True,text=True,timeout=30)
        if not allow_failure:self.assertEqual(0,result.returncode,result.stderr)
        return root,result

    def test_independent_type_static_nested_unused_and_unicode_positions(self):
        raw='''/* independent supplementary glyph: \U0001f3b5 */
package fixture;
import java.util.*;
import java.util.Map.*;
import static java.lang.Math.*;
import java.nio.file.*;
class Subject {
 List<String> values=List.of(); Entry<String,Integer> first;
 int calculate(int input){return max(abs(input),2);}
}
'''
        root,before=self.probe('original',{'Subject.java':raw})
        v=parse(before.stdout)['Subject.java']
        self.assertEqual({'import java.util.List;','import java.util.Map.Entry;','import static java.lang.Math.abs; import static java.lang.Math.max;',''}, {x[2]for x in v['imports']})
        candidate=replace_imports(raw,v['imports']);self.assertNotIn('.*;',candidate)
        _,after=self.probe('expanded',{'Subject.java':candidate})
        self.assertEqual(v['binding'],parse(after.stdout)['Subject.java']['binding'])
        self.assertEqual(v['declarations'],parse(after.stdout)['Subject.java']['declarations'])
        self.assertEqual(raw[raw.index('class Subject'):],candidate[candidate.index('class Subject'):])
        self.assertEqual(raw.splitlines()[0],candidate.splitlines()[0])
        self.assertEqual(root.joinpath('Subject.java').read_text(),raw)

    def test_inherited_static_and_local_method_shadowing(self):
        sources={'Parent.java':'package fixture; public class Parent {public static final int VALUE=7;}',
                 'Child.java':'package fixture; public class Child extends Parent {}',
                 'Subject.java':'package fixture; import static fixture.Child.*; import static java.lang.Math.*; class Subject { int value=VALUE; static int abs(int x){return x;} int use(){return abs(-1);} }'}
        _,before=self.probe('inherit',sources);v=parse(before.stdout)['Subject.java']
        self.assertEqual({'import static fixture.Child.VALUE;',''},{x[2]for x in v['imports']})
        sources['Subject.java']=replace_imports(sources['Subject.java'],v['imports'])
        _,after=self.probe('inherit-expanded',sources)
        self.assertEqual({k:x['binding']for k,x in parse(before.stdout).items()},{k:x['binding']for k,x in parse(after.stdout).items()})

    def test_ambiguous_unknown_or_changed_span_refused(self):
        for name,raw in [('ambiguous','import java.util.*; import java.awt.*; class Bad {List<String> a;}'),('unknown','import nonexistent.package0.*; class Bad {}')]:
            _,value=self.probe(name,{'Bad.java':raw},True);self.assertNotEqual(0,value.returncode);self.assertEqual('',value.stdout)
        for edits in [[(0,5,'')],[(0,21,''),(0,21,'')]]:
            with self.assertRaises(ValueError):replace_imports('import java.util.*; class X{}',edits)


if __name__=='__main__':unittest.main()
