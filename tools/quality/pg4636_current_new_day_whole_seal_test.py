"""Execute actual emitted save-before-parse/compare blocks with independent bad vectors."""
import ast
import json
import types
import unittest
from pyflakes.api import check
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as acceptance
from pg3870_current_resume_composite_test import constants


class RawWholeSeal(unittest.TestCase):
    def raw(self):return acceptance.seal_payload(admission.live(),admission.before())

    def test_actual_sql_bytes_survive_parse_refusal(self):
        source=self.raw();tree=ast.parse(source);capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
        index=next(i for i,n in enumerate(capture.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='sql_raw'for t in n.targets))
        block=ast.Module(body=capture.body[index:index+3],type_ignores=[]);saved=[]
        ns={'command':lambda args,bound:b'not JSON\n','sql':'fixed independent SQL','time':types.SimpleNamespace(monotonic_ns=lambda:123),'preserve_raw':lambda label,data:saved.append((label,data)),'rs':{},'json':json}
        with self.assertRaises(json.JSONDecodeError):exec(compile(block,'<actual raw-first SQL path>','exec'),ns)
        self.assertEqual([('sql-123',b'not JSON\n')],saved)

    def test_actual_unequal_complete_snapshots_are_both_preserved(self):
        tree=ast.parse(self.raw());matches=[]
        for node in ast.walk(tree):
            if not isinstance(node,ast.Try):continue
            for i,n in enumerate(node.body):
                if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='current'for t in n.targets)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='capture':matches.append((node.body,i))
        self.assertEqual(1,len(matches));body,index=matches[0];last=next(i for i in range(index,len(body))if isinstance(body[i],ast.Expr)and isinstance(body[i].value,ast.Call)and isinstance(body[i].value.func,ast.Name)and body[i].value.func.id=='require')
        observations=iter([{'independent':'first'},{'independent':'changed'}]);saved=[]
        def require(value):
            if not value:raise ValueError('independent full mismatch')
        ns={'capture':lambda:next(observations),'preserve_raw':lambda label,data:saved.append((label,json.loads(data))),'json':json,'require':require}
        helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='strict_equal')
        exec(compile(ast.Module(body=[helper],type_ignores=[]),'<actual strict full image comparator>','exec'),ns)
        with self.assertRaises(ValueError):exec(compile(ast.Module(body=body[index:last+1],type_ignores=[]),'<actual full first/second before equality>','exec'),ns)
        self.assertEqual([('complete-first',{'independent':'first'}),('complete-second',{'independent':'changed'})],saved)

    def test_whole_namespace_new_day_oracle_and_genuine_guard_remain_distinct(self):
        source=self.raw();self.assertEqual(0,check(source,'<whole new day raw-first source>'))
        values=constants(source);oracle=values['ORACLE'];self.assertIn('def qualify_new_day',oracle)
        self.assertIn("targets={'CLEAN_NOTIFICATION':len(expected['notifications'])",oracle)
        self.assertNotIn('require(all(history.values()))',oracle)
        self.assertIn('genuineRootDone',values['GUARD'])
        self.assertIn("RAW_SAVE=BASE/'pg4636-current-whole-seal-v1-raw'",source)
        self.assertLess(source.index("preserve_raw('captured-'"),source.index(" business=types.ModuleType('independent_sql')"))


if __name__=='__main__':unittest.main()
