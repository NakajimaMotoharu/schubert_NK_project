"""Actual emitted metadata close/receipt control flow; old transport is always UNKNOWN."""
import ast
import datetime
import hashlib
import json
import types
import unittest
from pyflakes.api import check,checkPath
import pg4648_composite_artifact_requalification as artifact


class ArtifactRecovery(unittest.TestCase):
    def scope(self,changed=False,close_error=False):
        raw=artifact.payload();nodes=ast.parse(raw).body
        first=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets))
        selected=nodes[first:];events=[];saved=[]
        image={'units':{f'unit{i}':{}for i in range(10)},'genuineCompletion':{'genuineRootDone':True,'completionCode':10},'doneEndUtc':'2026-10-17T00:00:00Z','businessOracle':{'exactRootBrowserCurrentChain':True}}
        def require(value):
            if not value:raise ValueError('independent current mismatch')
        def unref(unit):
            events.append(('unref',unit))
            if close_error:raise RuntimeError('independent close unknown')
        def persist(name,raw):events.append(('persist',name));saved.append(json.loads(raw))
        def current(label):return {'observed':'changed'if changed and label=='second'else'fixed'}
        ns={'manager':types.SimpleNamespace(LoadUnit=lambda u:events.append(('load',u)),RefUnit=lambda u:events.append(('ref',u)),UnrefUnit=unref),
          'bus':types.SimpleNamespace(close=lambda:events.append(('close',None))),'refs':[],'image':image,'current':current,'require':require,'strict_equal':lambda a,b:json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),
          'SOURCE':'literal-source','IMAGE_SHA':'literal-sha','others':[],'json':json,'datetime':datetime,'persist':persist,'print':lambda value:None}
        if close_error:
            with self.assertRaises(RuntimeError):exec(compile(ast.Module(body=selected,type_ignores=[]),'<actual close-unknown terminal suppression>','exec'),ns)
            self.assertEqual([],saved)
        else:
            with self.assertRaises(SystemExit)as stopped:exec(compile(ast.Module(body=selected,type_ignores=[]),'<actual normal/mismatch durable terminal>','exec'),ns)
            self.assertEqual(1 if changed else 0,stopped.exception.code)
            self.assertEqual(1,len(saved));self.assertTrue(saved[0]['originalCompositeExitUnknown']);self.assertFalse(saved[0]['oldUnknownNormalized']);self.assertFalse(saved[0]['originalCompositeReplayed'])
            self.assertEqual(not changed,saved[0]['savedThreeImagesRequalified']);self.assertTrue(saved[0]['newTenRefsNormalClose'])
            self.assertEqual(10,len([e for e in events if e[0]=='unref']))
            self.assertLess(events.index(('close',None)),events.index(('persist','terminal.safe.json')))

    def test_normal_new_scope_receipt_after_all_closes(self):self.scope()
    def test_mismatch_is_failed_but_new_scope_closes(self):self.scope(changed=True)
    def test_close_unknown_never_writes_success_or_terminal(self):self.scope(close_error=True)

    def test_actual_four_original_artifact_bytes_not_merely_same_row_count(self):
        nodes=ast.parse(artifact.payload()).body
        loop=next(n for n in nodes if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='path'and isinstance(n.iter,ast.Name)and n.iter.id=='paths')
        blob=b'{"independent":"fixed original data"}';digest=hashlib.sha256(blob).hexdigest()
        for changed in [False,True]:
            values={'first':blob,'second':b'changed'if changed else blob,'final':blob,'primary':blob}
            def require(value):
                if not value:raise ValueError('independent original byte mismatch')
            ns={'paths':list(values),'private':values.__getitem__,'IMAGE_SHA':digest,'original':None,'hashlib':hashlib,'require':require}
            if changed:
                with self.assertRaises(ValueError):exec(compile(ast.Module(body=[loop],type_ignores=[]),'<actual retained original bytes>','exec'),ns)
            else:
                exec(compile(ast.Module(body=[loop],type_ignores=[]),'<actual retained original bytes>','exec'),ns);self.assertEqual(blob,ns['original'])

    def test_small_complete_namespace_and_no_timeout_kill_replay(self):
        raw=artifact.payload();self.assertLess(len(raw),32768);self.assertEqual(0,check(raw,'<artifact current fresh scope>'))
        self.assertEqual(0,checkPath('tools/quality/pg4648_composite_artifact_requalification.py'))
        self.assertNotIn('CHAIN=',raw);self.assertIn('originalCompositeExitUnknown',raw)
        source=__import__('inspect').getsource(artifact.main)
        self.assertIn('child.wait()',source);self.assertIn("'ssh':process(child.pid)",source)
        self.assertNotIn('timeout=',source);self.assertNotIn('.kill(',source);self.assertNotIn('.terminate(',source)
        self.assertLess(raw.index("persist(label+'-sql.private.jsonl'"),raw.index("for line in r.stdout.splitlines()"))


if __name__=='__main__':unittest.main()
