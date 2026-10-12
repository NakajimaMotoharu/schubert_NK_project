"""Real FD fixture: retained bytes/identity, never fabricated Root/VM authority."""
import hashlib
import os
from pathlib import Path
import tempfile
import time
import types
import unittest
from pg1552_publication_inventory import capture

def metadata(fd):
    s=os.fstat(fd);return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def attrs(fd):return tuple((n,os.getxattr(fd,n))for n in sorted(os.listxattr(fd)))
def record(fd,payload=None):return {'metadata':list(metadata(fd)),'sha256':hashlib.sha256(payload).hexdigest()if payload is not None else None,'target':None,'acl':[n for n,_ in attrs(fd)]}

class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='pg1552-real-fd-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'approval';self.root.mkdir();self.path=self.root/'current';self.path.write_bytes(b'OLD-SIGNED')
        self.dir=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY);self.fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW)
        self.addCleanup(os.close,self.fd);self.addCleanup(os.close,self.dir)
        self.fixed={str(self.root):record(self.dir),str(self.path):record(self.fd,b'OLD-SIGNED')}
        self.before={str(self.root):self.fixed};self.actual={str(self.root):dict(self.fixed)}
        def validate(path,fixed,now,phase,actual,begin,end):
            a=fixed['metadata'];b=now['metadata']
            if phase=='before':
                if now!=fixed:raise ValueError('before mutated')
            elif path==str(self.path):
                if b[:5]!=a[:5]or b[5]!=0 or b[6:8]!=a[6:8]or not begin<=b[8]<=end or now['sha256']!=hashlib.sha256(b'OLD-SIGNED').hexdigest():raise ValueError('retained approval mutated')
            else:
                if now!=actual[str(self.root)][path]or b[:7]!=a[:7]or not all(begin<=b[i]<=end for i in [7,8]):raise ValueError('parent changed beyond allowed')
        self.oracle=types.SimpleNamespace(APPROVAL=str(self.root),CURRENT='/nonexistent-fixed-fixture-current',PHASES=['before','approval'],verify_retained=validate)
        self.contract=types.SimpleNamespace(metadata=metadata,attributes=attrs)
        self.inv=types.SimpleNamespace(root=str(self.root),root_fd=self.dir,closed=False,records={'current':{'size':10,'sha256':hashlib.sha256(b'OLD-SIGNED').hexdigest()}},held=[(self.dir,None,str(self.root),metadata(self.dir),attrs(self.dir)),(self.fd,self.dir,'current',metadata(self.fd),attrs(self.fd))])

    def test_before_full_hash_and_actual_fd(self):
        value=capture(self.inv,self.contract,self.oracle,self.before,self.actual,'before',0,time.time_ns())
        self.assertEqual(value[-1][3],hashlib.sha256(b'OLD-SIGNED').hexdigest());self.assertEqual(value[-1][1][1],os.fstat(self.fd).st_ino)

    def test_same_size_payload_tamper_refused(self):
        self.path.write_bytes(b'NEW-TAMPER')
        with self.assertRaises(ValueError):capture(self.inv,self.contract,self.oracle,self.before,self.actual,'before',0,time.time_ns())

    def test_real_atomic_detached_approval_still_validates_old_bytes(self):
        begin=time.time_ns();p=self.root/'part';p.write_bytes(b'NEW-SIGNED');os.replace(p,self.path);end=time.time_ns()
        newfd=os.open(self.path,os.O_RDONLY)
        try:self.actual={str(self.root):{str(self.root):record(self.dir),str(self.path):record(newfd,b'NEW-SIGNED')}}
        finally:os.close(newfd)
        v=capture(self.inv,self.contract,self.oracle,self.before,self.actual,'approval',begin,end)
        self.assertEqual(v[-1][1][5],0);self.assertEqual(v[-1][3],hashlib.sha256(b'OLD-SIGNED').hexdigest());self.assertEqual(self.path.read_bytes(),b'NEW-SIGNED')
        self.actual[str(self.root)][str(self.path)]['metadata'][1]+=1
        with self.assertRaises(ValueError):capture(self.inv,self.contract,self.oracle,self.before,self.actual,'approval',begin,end)

    def test_acl_and_closed_scope_refused(self):
        self.contract.attributes=lambda fd:(('foreign',b'value'),)
        with self.assertRaises(ValueError):capture(self.inv,self.contract,self.oracle,self.before,self.actual,'before',0,time.time_ns())
        self.inv.closed=True
        with self.assertRaises(ValueError):capture(self.inv,self.contract,self.oracle,self.before,self.actual,'before',0,time.time_ns())

if __name__=='__main__':unittest.main()
