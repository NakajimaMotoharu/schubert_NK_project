"""Actual BOM barrier, literal one-start argv, full64 preservation and normal old data only."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pyflakes.api import check,checkPath
import pg4736_new_normal_root_once as entry


class NormalRoot(unittest.TestCase):
    def test_actual_bom_barrier_before_once_reservation_and_old_data_label(self):
        nodes=ast.parse(entry.action()).body
        i=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)
               and ast.unparse(n.value.func)=='persist'and n.value.args[0].value=='external-start-guard.private.json')
        piece=ast.Module(body=nodes[i-1:i+1],type_ignores=[])
        literal=b'{"literal":"independent BOM bytes"}\n';digest=hashlib.sha256(literal).hexdigest()
        with tempfile.TemporaryDirectory()as directory:
            path=Path(directory)/'manifest';path.write_bytes(literal)
            for data,sha,valid in [(literal,digest,True),(b'foreign',digest,False),(literal,'0'*64,False)]:
                records=[]
                def require(value):
                    if value is not True:raise ValueError('BOM refused')
                ns={'manifest_path':path,'manifest':data,'sha':sha,'hashlib':hashlib,'require':require,
                    'data':{'source':{'commit':entry.SOURCE}},'summary':{'genuineParentDone':True,'completionCode':10},
                    'watch':{'pid':123},'persist':lambda name,value:records.append((name,value))}
                if valid:
                    exec(compile(piece,'<actual reservation barrier>','exec'),ns)
                    self.assertEqual(1,len(records));guard=records[0][1]
                    self.assertEqual(digest,guard['manifestSha256']);self.assertTrue(guard['previousRootDataOnly'])
                    self.assertTrue(guard['previousNormalRootData']['genuineParentDone']);self.assertFalse(guard['replayAllowed'])
                    self.assertEqual(1800,guard['originalBudgetSeconds']);json.dumps(guard)
                else:
                    with self.assertRaises(ValueError):exec(compile(piece,'<actual reservation barrier>','exec'),ns)
                    self.assertEqual([],records)

    def test_actual_one_start_full64_scope_and_output_after_refs(self):
        hashes={n:hashlib.sha256(v.encode()).hexdigest()for n,v in entry.observer.files().items()}
        raw=entry.payload(hashes);self.assertEqual(0,check(raw,'<full normal root once>'))
        calls=[ast.literal_eval(n.args[0])for n in ast.walk(ast.parse(entry.action()))
               if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and ast.unparse(n.func)=='subprocess.run']
        self.assertEqual([['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']],calls)
        self.assertIn('require(len(records)==64)',raw)
        self.assertIn('previousRootDataOnly',raw);self.assertNotIn('previousFailedRootData',raw)
        self.assertNotIn("'parentExit':143",raw)
        self.assertIn("'--resume'not in declaration",raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index('for unit in reversed(refs):manager.UnrefUnit(unit)'),raw.index('current.update(observedUTC='))
        self.assertIn(entry.SOURCE,raw);self.assertIn(entry.BOM,raw)
        self.assertEqual(0,checkPath(entry.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
