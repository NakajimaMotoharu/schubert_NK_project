"""Independent literal source/epoch, actual BOM barrier and immutable observer closure."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pyflakes.api import check
import pg4560_current_same_peer_observer as observer
import pg4576_current_fresh_noargs_once as entry
import pg4578_current_live_binding as binding


class FreshCurrent(unittest.TestCase):
    def test_actual_bom_barrier_precedes_durable_once_reservation(self):
        nodes=ast.parse(entry.action()).body
        index=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='persist'and n.value.args[0].value=='external-start-guard.private.json')
        actual=ast.Module(body=nodes[index-1:index+1],type_ignores=[])
        blob=b'{"independent":"BOM byte fixture"}\n';digest=hashlib.sha256(blob).hexdigest()
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'manifest';path.write_bytes(blob)
            for raw,sha,valid in [(blob,digest,True),(b'changed',digest,False),(blob,'0'*64,False)]:
                saved=[]
                def require(ok):
                    if ok is not True:raise ValueError('BOM refused')
                ns={'manifest':path,'raw':raw,'sha':sha,'hashlib':hashlib,'require':require,'data':{'source':{'commit':'literal'}},'summary':{'parentNormal':False},'watch':{'pid':123},'persist':lambda name,v:saved.append((name,v))}
                if valid:
                    exec(compile(actual,'<real BOM barrier>','exec'),ns)
                    self.assertEqual([('external-start-guard.private.json',{'source':'literal','manifestSha256':digest,'ordinaryNoargs':True,'oldRunNotResumed':True,'previousFailedRootData':{'parentNormal':False},'originalBudgetSeconds':1800,'attemptReserved':True,'replayAllowed':False,'observer':{'pid':123}})],saved)
                    json.dumps(saved)
                else:
                    with self.assertRaises(ValueError):exec(compile(actual,'<real BOM barrier>','exec'),ns)
                    self.assertEqual([],saved)

    def test_source_and_all_four_observer_files(self):
        self.assertEqual('964e96e45bb588e7e75798b5adf425cbd9985427',entry.SOURCE)
        self.assertEqual('93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',entry.BOM)
        files=observer.files();ns=observer.namespace()
        self.assertEqual(files,ns['files']());self.assertEqual(entry.SOURCE,ns['SOURCE']);self.assertEqual(entry.BOM,ns['DIGEST'])
        self.assertEqual({'pg4560_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py','pg4216_same_peer_observer_manager.py'},set(files))
        for name,raw in files.items():self.assertEqual(0,check(raw,name));compile(raw,name,'exec')
        watch=files['pg4560_watch_parent.py']
        self.assertIn('reader.read(UNITS[role])',watch)
        self.assertIn('ExecMainStartTimestampMonotonic',watch)
        self.assertIn('+1860',watch);self.assertIn('same(roots[role],aa)',watch)
        self.assertIn('owned.intersection(sockets',watch)

    def test_actual_entry_one_start_no_resume_no_permit_authority(self):
        hashes={n:hashlib.sha256(v.encode()).hexdigest()for n,v in observer.files().items()}
        raw=entry.payload(hashes);self.assertEqual(0,check(raw,'<whole entry>'))
        tree=ast.parse(entry.action());starts=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=='run':starts.append(ast.literal_eval(node.args[0]))
        self.assertEqual([['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']],starts)
        self.assertIn('require(len(records)==58)',raw)
        self.assertIn("oracle['canonical_epoch'](epoch);require(epoch==expected_epoch)",raw)
        self.assertIn("not os.path.lexists(Path('/run/schubert-nk/startup')/(epoch_id+'.permit'))",raw)
        self.assertNotIn('former_issued',raw)
        self.assertIn("native==snapshot()['native']",raw)
        self.assertNotIn('hashlib.sha256(manifest)',raw)
        self.assertIn('ordinaryNoargs',raw);self.assertIn('--resume\'not in declaration',raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index('for unit in reversed(refs):manager.UnrefUnit(unit)'),raw.index('current.update(observedUTC='))

    def test_actual_live_binding_source_generation_and_whole_namespace(self):
        raw=binding.body();self.assertEqual(0,check('SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n'+raw,'<actual live>'))
        self.assertIn('PG4432',raw);self.assertNotIn('PG3976',raw)
        self.assertIn("fields[1]!='b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1'",raw)
        self.assertIn("unit['InvocationID']!='bbcdb69957764d489a9c757b441542fd'",raw)


if __name__=='__main__':unittest.main()
