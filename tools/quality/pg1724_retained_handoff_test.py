"""Independent guards, actual kernel queue, no guest or signal calls."""
import ast
import copy
import fcntl
import os
from pathlib import Path
import tempfile
import unittest
from pg1724_retained_host_gate import queued_gate,identity,current_owner
from pg1673_sole_owner_contract import fresh_sole_parent
from pg1724_bootstrap_retained_once_handoff import payload

class ContractTest(unittest.TestCase):
    def test_kernel_queue_preserves_existing_lock(self):
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'gate';fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600)
            try:
                fcntl.flock(fd,fcntl.LOCK_EX)
                def owned(p):
                    self.assertEqual(p,path);self.assertEqual(identity(fd,p),(path.stat().st_dev,path.stat().st_ino))
                with queued_gate(path,owned)as acquired:
                    self.assertFalse(acquired.wait(.05))
                    fcntl.flock(fd,fcntl.LOCK_UN)
                    self.assertTrue(acquired.wait(2))
                    other=os.open(path,os.O_RDWR)
                    try:
                        with self.assertRaises(BlockingIOError):fcntl.flock(other,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    finally:os.close(other)
                fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            finally:os.close(fd)
    def test_gate_namespace_and_mode_rejected(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'one';q=Path(d)/'two';p.touch(mode=0o600);q.touch(mode=0o600)
            fd=os.open(p,os.O_RDWR)
            try:
                with self.assertRaises(ValueError):identity(fd,q)
                p.chmod(0o644)
                with self.assertRaises(ValueError):identity(fd,p)
            finally:os.close(fd)
    def test_current_owner_missing_gate_rejected(self):
        with self.assertRaises((OSError,ValueError)):current_owner(Path('/nonexistent-pg1724-gate'))
    def test_complete_actor_contract(self):
        actor={'pid':383695,'ticks':7281859,'argvSha256':'a'*64,'authority':{'Uid':'0'},'cgroup':'fixed','fds':{str(i):{'metadata':[28,i,0,0,16832,1,64,100,100],'target':'fixture'}for i in range(99)}}
        for n in ('29','32'):actor['fds'][n]={'metadata':[28,1,0,0,16877,1,64,100,100],'target':'/run'}
        self.assertTrue(fresh_sole_parent(actor,copy.deepcopy(actor),101))
        newer=copy.deepcopy(actor)
        for n in ('29','32'):newer['fds'][n]['metadata'][7:]=[101,101]
        self.assertTrue(fresh_sole_parent(actor,newer,101))
        for k in ('pid','ticks','argvSha256','authority','cgroup'):
            bad=copy.deepcopy(actor);bad[k]=None
            with self.subTest(field=k),self.assertRaises(ValueError):fresh_sole_parent(actor,bad,101)
        for kind in ('missing','extra','target','inode','timeback','timefuture','bool'):
            bad=copy.deepcopy(actor)
            if kind=='missing':del bad['fds']['10']
            elif kind=='extra':bad['fds']['100']=bad['fds']['10']
            elif kind=='target':bad['fds']['10']['target']='foreign'
            elif kind=='inode':bad['fds']['29']['metadata'][1]=999
            elif kind=='timeback':bad['fds']['29']['metadata'][7]=99
            elif kind=='timefuture':bad['fds']['29']['metadata'][7]=102
            else:bad['fds']['10']['metadata'][0]=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):fresh_sole_parent(actor,bad,101)
    def test_generated_signal_boundary(self):
        raw=payload();self.assertEqual(raw.count('terminate(383695,7281859,before,reserve,os.pidfd_open,send,wait,os.close)'),1)
        self.assertLess(raw.index("private('fresh-complete.private'"),raw.index('terminate(383695'))
        self.assertIn('signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)',raw)
        # Frozen Unit configuration may contain a KillSignal value; distinguish
        # configuration evidence from an executable signal request.
        self.assertFalse(any(isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='signal'and n.attr=='SIGKILL'for n in ast.walk(ast.parse(raw))))
        self.assertFalse('pg_terminate_backend' in raw)
        self.assertIn("refs=new References",(Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1719-current-bootstrap-tools-v1/Pg1719BootstrapExisting.java')).read_text())

if __name__=='__main__':unittest.main()
