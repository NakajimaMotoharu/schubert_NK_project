import copy
import json
import unittest
from pyflakes.api import checkPath
import pg5568_monitor_bytecode as entry


class ActualPrivateMonitor(unittest.TestCase):
    def test_actual_six_role_paths_are_bom_bound_before_any_output(self):
        jars=entry.release_jars(entry.W/'pg5430-release-v1')
        self.assertEqual(set(jars),{'api','web','batch','bootstrap','protocol','storage'})
        self.assertEqual(jars['batch'].relative_to(entry.W/'pg5430-release-v1').as_posix(),'operations/batch.jar')
        self.assertIn('/api/lib/',str(jars['bootstrap']))
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory()as folder:
            (Path(folder)/'RELEASE-MANIFEST.json').write_text('{}')
            with self.assertRaises(ValueError):entry.release_jars(Path(folder))

    def test_only_private_field_entered_and_body_guarded_on_all_exits(self):
        method={'header':'public void status();','ops':[(0,'aload_0',''),(1,'getfield','// Field stateLock:Ljava/lang/Object;'),
            (4,'dup',''),(5,'astore_1',''),(6,'monitorenter',''),(7,'aload_0',''),(8,'monitorexit',''),(9,'return',''),(10,'monitorexit','')],
            'handlers':[(7,8,10,'any')]}
        self.assertEqual(entry.private_monitor(method)['monitorEnterPc'],6)
        for alter in('exposed','wrongField','unguarded','noExceptionalExit'):
            bad=copy.deepcopy(method)
            if alter=='exposed':bad['header']='public synchronized void status();'
            if alter=='wrongField':bad['ops'][1]=(1,'getfield','// Field other:Ljava/lang/Object;')
            if alter=='unguarded':bad['handlers']=[]
            if alter=='noExceptionalExit':bad['ops'].pop()
            with self.assertRaises(ValueError):entry.private_monitor(bad)

    def test_lock_must_precede_native_and_intent_and_have_single_allocation(self):
        method={'ops':[(0,'new','// class java/lang/Object'),(10,'invokeinterface','X$Intent.begin:()LX;'),(20,'invokeinterface','X$Start.execute:()LX;')]}
        self.assertEqual(entry.allocation_before_native(method,True)['lockNewPc'],0)
        for ops in(method['ops'][1:],method['ops'][1:]+method['ops'][:1],method['ops']+method['ops'][:1]):
            with self.assertRaises(ValueError):entry.allocation_before_native({'ops':ops},True)

    def test_all161_actual_source_statements_are_individually_bound(self):
        path=entry.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5560-snapshot-static-findings-v1/manifest.json'
        baseline=json.loads(path.read_bytes());rows,fields=entry.lexical_private_locks(baseline)
        self.assertEqual(len(rows),161);self.assertEqual(len(fields),47)
        broken=copy.deepcopy(baseline)
        next(r for r in broken['findings']if r['rule']=='AvoidSynchronizedStatement')['sourceSha256']='0'*64
        with self.assertRaises(ValueError):entry.lexical_private_locks(broken)
        for p in(entry.__file__,__file__):self.assertEqual(checkPath(p),0)


if __name__=='__main__':unittest.main()
