import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pyflakes.api import check,checkPath
import pg4892_new_normal_root_once as role


class Root(unittest.TestCase):
    def test_independent_preflight_source_window_and_before_sha_are_mandatory(self):
        now=datetime.datetime(2026,10,17,0,0,tzinfo=datetime.timezone.utc)
        proof={'actualExit':0,'source':role.SOURCE,'result':{'beforeSha256':'a'*64,'dbOrClockChanged':False,'rootStartIssued':False,'projections':[{'cutoff':now.isoformat(),'independentApplicability':True},{'cutoff':(now+datetime.timedelta(hours=2)).isoformat(),'independentApplicability':True}]}}
        role.oracle_applicable(proof,now,'a'*64)
        for key,value in [('actualExit',False),('source','f'*40)]:
            bad=copy.deepcopy(proof);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):role.oracle_applicable(bad,now,'a'*64)
        for key,value in [('dbOrClockChanged',True),('rootStartIssued',True),('beforeSha256','b'*64),('projections',[])]:
            bad=copy.deepcopy(proof);bad['result'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):role.oracle_applicable(bad,now,'a'*64)
        for shift in (-1,3):
            with self.assertRaises(ValueError):role.oracle_applicable(proof,now+datetime.timedelta(hours=shift),'a'*64)

    def test_actual_reservation_manifest_barrier_fixed1800_budget_old_data_only(self):
        nodes=ast.parse(role.action()).body
        index=next(i for i,n in enumerate(nodes) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='persist' and n.value.args[0].value=='external-start-guard.private.json')
        block=ast.Module(body=nodes[index-1:index+1],type_ignores=[])
        literal=b'{"independent":"fixed manifest bytes"}\n';digest=hashlib.sha256(literal).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'manifest';path.write_bytes(literal)
            for data,sha,valid in ((literal,digest,True),(b'foreign',digest,False),(literal,'0'*64,False)):
                records=[]
                def require(value):
                    if value is not True:raise ValueError('actual barrier refused')
                ns={'manifest_path':path,'manifest':data,'sha':sha,'hashlib':hashlib,'require':require,'data':{'source':{'commit':role.SOURCE}},'summary':{'genuineParentDone':True,'completionCode':10},'watch':{'pid':123},'persist':lambda name,value:records.append((name,value))}
                if valid:
                    exec(compile(block,'<actual reservation>','exec'),ns)
                    self.assertEqual(1,len(records));guard=records[0][1];self.assertTrue(guard['previousRootDataOnly']);self.assertFalse(guard['replayAllowed']);self.assertEqual(1800,guard['originalBudgetSeconds']);self.assertEqual(digest,guard['manifestSha256']);json.dumps(guard)
                else:
                    with self.assertRaises(ValueError):exec(compile(block,'<actual reservation>','exec'),ns)
                    self.assertEqual([],records)

    def test_one_start_all72_and_result_only_after_normal_metadata_close(self):
        hashes={n:hashlib.sha256(v.encode()).hexdigest() for n,v in role.observer.files().items()}
        raw=role.payload(hashes);self.assertEqual(0,check(raw,'<actual new ordinary Root>'))
        calls=[ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse(role.action())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='subprocess.run']
        self.assertEqual([['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']],calls)
        for text in ('require(len(records)==72)','previousRootDataOnly',"'--resume'not in declaration",role.SOURCE,role.BOM):self.assertIn(text,raw)
        self.assertNotIn('previousFailedRootData',raw);self.assertNotIn("'parentExit':143",raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index('for unit in reversed(refs):manager.UnrefUnit(unit)'),raw.index('current.update(observedUTC='))
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
