"""Independent296 ordinary-entry invariants; no real start/permit or old native credit."""
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5464_new_current_readonly as current
import pg5466_new_current_same_peer_observer as observer
import pg5468_new_day_query_preflight as oracle
import pg5470_new_normal_root_once as entry
import pg5472_new_normal_live_binding as binding


class Root(unittest.TestCase):
    def test_new_current_full88_capacity_and_no_old_credit(self):
        raw=current.payload()
        for marker in(current.SOURCE,current.BOM,current.AFTER,current.context(),"'native88Preserved':True","'newRootNotStarted':True","'oldNativeCredit':False",'12884901888'):
            self.assertIn(marker,raw)
        self.assertEqual(check(raw,'<current296 readonly>'),0)
        original=json.loads((current.post.role.W/current.post.SLOT/'manifest.safe.json').read_bytes())
        for key,value in(('productionSource',current.post.role.CURRENT),('originalBackupNative88Preserved',False),('newSourceParentNotStarted',False),('newTenReferencesReturnedNormally',False)):
            bad=copy.deepcopy(original);bad['result'][key]=value
            with patch.object(current.json,'loads',return_value=bad),self.assertRaises(ValueError):current.context()

    def test_exact_four_observer_files_current_peer_and_normal_lifetime(self):
        values,ns=observer.files(),observer.namespace()
        self.assertEqual(ns['SOURCE'],observer.SOURCE);self.assertEqual(ns['DIGEST'],observer.BOM);self.assertEqual(ns['files'](),values)
        self.assertEqual(set(values),{'pg5466_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py','pg4216_same_peer_observer_manager.py'})
        for name,raw in values.items():self.assertEqual(check(raw,name),0)
        for marker in('reader.read(UNITS[role])','observerTenMetadataRefsNormalClose'):self.assertIn(marker,values['pg5466_watch_parent.py'])
        self.assertIn('pg5460-ownership-publication-independent-post-v1',observer.source())
        self.assertIn('PG5430',observer.source());self.assertNotIn('PG4980',observer.source())

    def test_independent_twohour_before_window_and_key_redaction(self):
        raw=oracle.payload();self.assertEqual(check(raw,'<actual296 before window>'),0)
        for marker in(current.AFTER,current.context(),current.BOM,'now+datetime.timedelta(hours=2)',"'rootStartIssued':False","'plaintextLogged':False","'dbOrClockChanged':False",r"KEY[:]=b'\0'*len(KEY)"):
            self.assertIn(marker,raw)
        self.assertNotIn('pg5014-ssc304-publication-independent-post-v1',raw)

    def test_foreign_source_bad_window_or_before_never_authorizes_start(self):
        now=datetime.datetime(2026,10,19,0,0,tzinfo=datetime.timezone.utc)
        proof={'actualExit':0,'source':entry.SOURCE,'result':{'beforeSha256':'a'*64,'dbOrClockChanged':False,'rootStartIssued':False,
            'projections':[{'cutoff':now.isoformat(),'independentApplicability':True},{'cutoff':(now+datetime.timedelta(hours=2)).isoformat(),'independentApplicability':True}]}}
        entry.oracle_applicable(proof,now,'a'*64)
        for key,value in(('actualExit',False),('source','f'*40)):
            with self.assertRaises(ValueError):entry.oracle_applicable({**proof,key:value},now,'a'*64)
        for key,value in(('dbOrClockChanged',True),('rootStartIssued',True),('beforeSha256','b'*64),('projections',[])):
            bad=copy.deepcopy(proof);bad['result'][key]=value
            with self.assertRaises(ValueError):entry.oracle_applicable(bad,now,'a'*64)
        for shift in(-1,3):
            with self.assertRaises(ValueError):entry.oracle_applicable(proof,now+datetime.timedelta(hours=shift),'a'*64)

    def test_manifest_barrier_before_durable_reservation_and_same1800_budget(self):
        nodes=ast.parse(entry.action()).body
        index=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and ast.unparse(n.value.func)=='persist'and n.value.args[0].value=='external-start-guard.private.json')
        block=ast.Module(body=nodes[index-1:index+1],type_ignores=[]);literal=b'{"independent":"fixed bytes"}\n';digest=hashlib.sha256(literal).hexdigest()
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'manifest';path.write_bytes(literal)
            for data,sha,valid in((literal,digest,True),(b'foreign',digest,False),(literal,'0'*64,False)):
                records=[]
                def require(value):
                    if value is not True:raise ValueError('independent barrier refused')
                ns={'manifest_path':path,'manifest':data,'sha':sha,'hashlib':hashlib,'require':require,'data':{'source':{'commit':entry.SOURCE}},
                    'summary':{'genuineParentDone':True,'completionCode':10},'watch':{'pid':123},'persist':lambda name,value:records.append((name,value))}
                if valid:
                    exec(compile(block,'<durable guarded reservation>','exec'),ns);self.assertEqual(len(records),1)
                    guard=records[0][1];self.assertTrue(guard['previousRootDataOnly']);self.assertFalse(guard['replayAllowed']);self.assertEqual(guard['originalBudgetSeconds'],1800);self.assertEqual(guard['manifestSha256'],digest);json.dumps(guard)
                else:
                    with self.assertRaises(ValueError):exec(compile(block,'<durable guarded reservation>','exec'),ns)
                    self.assertEqual(records,[])

    def test_exact_one_start_all88_and_success_after_returned_refs(self):
        hashes={name:hashlib.sha256(raw.encode()).hexdigest()for name,raw in observer.files().items()}
        raw=entry.payload(hashes);self.assertEqual(check(raw,'<whole296 ordinary Root once>'),0)
        calls=[ast.literal_eval(n.args[0])for n in ast.walk(ast.parse(entry.action()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and ast.unparse(n.func)=='subprocess.run']
        self.assertEqual(calls,[['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']])
        for marker in('require(len(records)==88)','previousRootDataOnly',"'--resume'not in declaration",entry.SOURCE,entry.BOM):self.assertIn(marker,raw)
        self.assertNotIn("'parentExit':143",raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index('for unit in reversed(refs):manager.UnrefUnit(unit)'),raw.index('current.update(observedUTC='))

    def test_same_new_once_binding_historical_negative_ids_not_rebound(self):
        raw=binding.body();self.assertEqual(check('SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n'+raw,'<same296 binding>'),0)
        self.assertEqual(binding.ONCE,entry.SLOT);self.assertIn('0.1.0-PG5430',raw);self.assertNotIn('pg5022-new-normal-root-once-v1',raw)
        self.assertIn('fff841d9-2554-4680-b17d-9548bfa79cbb',raw);self.assertIn("unit['InvocationID']!='b414b0e1e5ac47e8b5fb8c5ae3d94348'",raw)
        for item in(current,observer,oracle,entry,binding):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
