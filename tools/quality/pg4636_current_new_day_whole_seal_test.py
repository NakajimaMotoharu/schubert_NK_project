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
        self.assertIn("RAW_SAVE=BASE/'pg4642-current-whole-seal-v1-raw'",source)
        qualified=acceptance.terminal_payload(admission.live());marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+acceptance.TERM+"')"
        self.assertEqual(qualified[:qualified.index(marker)],values['GUARD'])
        for literal in ['964e96e45bb588e7e75798b5adf425cbd9985427','93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de','0.1.0-PG4432']:
            self.assertIn(literal,values['GUARD'])
        self.assertNotIn('0.1.0-PG3976',values['GUARD'])
        self.assertLess(source.index("preserve_raw('captured-'"),source.index(" business=types.ModuleType('independent_sql')"))

    def test_actual_genuine_guard_rejects_old_release_source_and_bom(self):
        guard=constants(self.raw())['GUARD'];nodes=ast.parse(guard).body
        index=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='release'for t in n.targets))
        block=ast.Module(body=nodes[index:index+3],type_ignores=[])
        for link,source,digest,accepted in [
          ('/opt/schubert-nk/releases/0.1.0-PG4432','964e96e45bb588e7e75798b5adf425cbd9985427','93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',True),
          ('/opt/schubert-nk/releases/0.1.0-PG3976','964e96e45bb588e7e75798b5adf425cbd9985427','93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',False),
          ('/opt/schubert-nk/releases/0.1.0-PG4432','7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',False),
          ('/opt/schubert-nk/releases/0.1.0-PG4432','964e96e45bb588e7e75798b5adf425cbd9985427','0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',False)]:
            blob=json.dumps({'source':{'commit':source}}).encode()
            class File:
                def __truediv__(self,name):return self
                def read_bytes(self):return blob
                def readlink(self):return link
            def require(ok):
                if not ok:raise ValueError('independent source tuple refused')
            # Hash is a port here: this tests tuple selection, not SHA. Actual
            # signature/manifest SHA is independently exercised by the live post.
            ns={'pathlib':types.SimpleNamespace(Path=lambda path:File()),'json':json,'hashlib':types.SimpleNamespace(sha256=lambda value:types.SimpleNamespace(hexdigest=lambda:digest)),'require':require}
            with self.subTest(link=link,source=source,digest=digest):
                if accepted:exec(compile(block,'<actual source guard tuple barrier>','exec'),ns)
                else:
                    with self.assertRaises(ValueError):exec(compile(block,'<actual source guard tuple barrier>','exec'),ns)

    def test_actual_complete_image_comparator_rejects_bool_as_int(self):
        tree=ast.parse(self.raw());helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='strict_equal');ns={}
        exec(compile(ast.Module(body=[helper],type_ignores=[]),'<actual strict whole image type comparator>','exec'),ns)
        self.assertFalse(ns['strict_equal']({'counter':True},{'counter':1}))
        self.assertFalse(ns['strict_equal']({'counter':None},{'counter':0}))
        self.assertTrue(ns['strict_equal']({'rows':[{'counter':1}]},{'rows':[{'counter':1}]}))


if __name__=='__main__':unittest.main()
