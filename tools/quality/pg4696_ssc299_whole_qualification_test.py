"""Exact whole counts/case additions/closed physical diff and real XML refusal vectors."""
import ast
import hashlib
import inspect
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E
from pyflakes.api import check,checkPath
import pg4694_ssc299_full as full
import pg4696_ssc299_whole_qualification as q


class WholeSSC299(unittest.TestCase):
    def test_exact_physical_scope_and_foreign_byte_rejected(self):
        old={**{k:'0'*64 for k in q.MODIFIED},**{'batch:fixture/C'+str(i)+'.class':'0'*64 for i in range(1638)}}
        new={**old,**{k:'1'*64 for k in q.MODIFIED},**{k:'2'*64 for k in q.INTERFACES}}
        changes,unchanged=q.physical_difference(old,new,new)
        self.assertEqual(8,len(changes));self.assertEqual(1638,unchanged)
        for bad in [{**new,'batch:fixture/C0.class':'f'*64},{k:v for k,v in new.items()if k not in q.INTERFACES},{**new,'api:Unexpected.class':'0'*64},{**new,next(iter(q.MODIFIED)):False}]:
            with self.assertRaises(ValueError):q.physical_difference(old,bad,bad)
        with self.assertRaises(ValueError):q.physical_difference(old,new,{})

    def test_xml_false_success_is_rejected_and_exact_case_counts_bound(self):
        tree=ast.parse(q.qualifier_source());nodes=[n for n in tree.body[0].body if isinstance(n,ast.FunctionDef)and n.name in {'sha','need','identities'}]
        ns={'hashlib':hashlib,'E':E,'start':0};exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<actual standalone XML classifier>','exec'),ns)
        prefix='<testsuite tests="1" failures="0" errors="0" skipped="0">';case='<testcase classname="literal.Class" name="literalMethod"/>'
        with tempfile.TemporaryDirectory(prefix='ssc299-xml-')as directory:
            path=Path(directory)/'TEST-literal.xml';path.write_text(prefix+case+'</testsuite>');h={path.name:hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertEqual(({('literal.Class','literalMethod')},1),ns['identities'](Path(directory),h,True))
            for tag in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']:
                path.write_text(prefix+case.replace('/>','><'+tag+'/></testcase>')+'</testsuite>');h={path.name:hashlib.sha256(path.read_bytes()).hexdigest()}
                with self.assertRaises(ValueError):ns['identities'](Path(directory),h,True)
        raw=q.qualifier_source()
        for guard in ['len(oldcases) == 3721','len(additions) == 18','len(cases) == 3739',"== 549","old = base / 'runs/PG4420-six-v1'","out = base / 'runs/PG4694-six-v1'",'physical_difference(oldphysical, physical, data[']:
            self.assertIn(guard,raw)

    def test_real_eighteen_new_cases_full_source_and_standalone_globals(self):
        self.assertEqual(18,len(set(q.NEW_CASES)))
        for cls,method in q.NEW_CASES:
            path=full.ROOT/('src/schubert-nk-batch/src/test/java/'+cls.replace('.','/')+'.java')
            self.assertIn('void '+method+'(',path.read_text())
        self.assertEqual(0,check(full.server_source(full.SOURCE,'a'*64),'<fresh expected3739/549/1646>'))
        raw='import json\nMODIFIED=set()\nINTERFACES=set()\n'+inspect.getsource(q.physical_difference)+'\n'+q.qualifier_source()+'\nprint(json.dumps({}))\n'
        self.assertEqual(0,check(raw,'<whole independent newsource>'))
        self.assertEqual(0,checkPath(full.__file__));self.assertEqual(0,checkPath(q.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
