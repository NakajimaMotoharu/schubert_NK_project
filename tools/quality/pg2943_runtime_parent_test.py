"""Independent metadata/byte vectors for exact new-parent delta; no VM writes."""
import copy
import hashlib
import inspect
import os
import stat
import unittest
import pg2943_runtime_parent_contract as p


def directory(ino,links,size,mtime):return {'metadata':[1,ino,0,0,stat.S_IFDIR|0o755,links,size,mtime,mtime],'sha256':None}


class RuntimeParent(unittest.TestCase):
    def fixture(self):
        data=b'[Service]\nExecStart=fixed --resume original\n'
        before={p.ROOT:directory(10,2,40,100)}
        actual={p.ROOT:directory(10,3,60,210),p.DIRECTORY:directory(11,2,60,220),p.TARGET:{'metadata':[1,12,0,0,stat.S_IFREG|0o644,1,len(data),230,230],'sha256':hashlib.sha256(data).hexdigest()}}
        return before,actual,data

    def test_new_parent_and_retained_empty_parent_are_distinct(self):
        before,actual,data=self.fixture();self.assertTrue(p.runtime_tree(before,actual,data,200,300))
        before={p.ROOT:directory(10,3,60,100),p.DIRECTORY:directory(11,2,40,100)}
        actual[p.ROOT]=copy.deepcopy(before[p.ROOT]);self.assertTrue(p.runtime_tree(before,actual,data,200,300))

    def test_foreign_inode_owner_mode_time_extra_and_missing_refused(self):
        before,actual,data=self.fixture()
        for path,index,value in [(p.ROOT,1,99),(p.ROOT,2,1),(p.ROOT,5,4),(p.DIRECTORY,0,2),(p.DIRECTORY,1,10),(p.DIRECTORY,2,1),(p.DIRECTORY,4,stat.S_IFDIR|0o777),(p.DIRECTORY,7,199),(p.TARGET,1,11),(p.TARGET,5,2),(p.TARGET,6,0),(p.TARGET,8,301)]:
            bad=copy.deepcopy(actual);bad[path]['metadata'][index]=value
            self.assertFalse(p.runtime_tree(before,bad,data,200,300),(path,index))
        for bad in [{},None,{**actual,'foreign':directory(20,2,40,220)}]:self.assertFalse(p.runtime_tree(before,bad,data,200,300))
        bad=copy.deepcopy(actual);bad[p.TARGET]['sha256']='0'*64;self.assertFalse(p.runtime_tree(before,bad,data,200,300))

    def test_owned_parent_descriptor_order_and_partial_failure_retained(self):
        for fail in [False,True]:
            fake=FakeOs(fail)
            ns={'os':fake,'stat':stat}
            source=inspect.getsource(p.owned_create_parent).replace('    import os\n','')
            exec(compile(source,'<independent syscall fixture only>','exec'),ns)
            operation=lambda expected,unit='schubert-nk-morning-controller.service.d':ns['owned_create_parent'](expected,unit,require,fake.metadata,fake.named)
            expected=fake.metadata(13)
            if fail:
                with self.assertRaises(OSError):operation(expected)
                self.assertTrue(fake.created)
            else:
                result=operation(expected)
                self.assertEqual([0,0,stat.S_IFDIR|0o755,2],result[2:6])
                self.assertEqual([14,13],fake.synced)
            self.assertEqual([14,13,12,11,10],fake.closed)
            self.assertEqual(1,fake.mkdirCalls)
            with self.assertRaises(ValueError):operation(expected)
            self.assertEqual(1,fake.mkdirCalls) # No repair, deletion or second creation.

    def test_wrong_role_root_metadata_and_foreign_entries_refuse_before_create(self):
        for fault in ['uid','metadata','foreign','unit']:
            fake=FakeOs(False);fake.uid=1 if fault=='uid'else 0;fake.foreign=fault=='foreign'
            ns={'os':fake,'stat':stat};exec(inspect.getsource(p.owned_create_parent).replace('    import os\n',''),ns)
            expected=fake.metadata(13)
            if fault=='metadata':expected[1]=999
            with self.assertRaises(ValueError):ns['owned_create_parent'](expected,'foreign'if fault=='unit'else'schubert-nk-morning-controller.service.d',require,fake.metadata,fake.named)
            self.assertEqual(0,fake.mkdirCalls)


def require(value):
    if not value:raise ValueError('independent fixture contract denied')


class FakeOs:
    O_RDONLY=os.O_RDONLY;O_DIRECTORY=os.O_DIRECTORY;O_NOFOLLOW=os.O_NOFOLLOW;O_CLOEXEC=os.O_CLOEXEC
    def __init__(self,fail):
        self.fail=fail;self.uid=0;self.foreign=False;self.created=False;self.mkdirCalls=0;self.closed=[];self.synced=[];self.mode=0o700
    def geteuid(self):return self.uid
    def getegid(self):return 0
    def open(self,name,flags,dir_fd=None):
        require(flags==os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        return {'/':10,'run':11,'systemd':12,'system':13,'schubert-nk-morning-controller.service.d':14}[name]
    def metadata(self,fd):
        return [1,fd,0,0,stat.S_IFDIR|(self.mode if fd==14 else 0o755),2,40,100,100]
    def named(self,name,fd):return self.metadata(self.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,fd))
    def listxattr(self,fd):return []
    def listdir(self,fd):return ['foreign']if self.foreign else ['schubert-nk-morning-controller.service.d']if fd==13 and self.created else []
    def mkdir(self,name,mode,dir_fd=None):
        require(name=='schubert-nk-morning-controller.service.d'and mode==0o700 and dir_fd==13 and not self.created)
        self.created=True;self.mkdirCalls+=1
    def fchmod(self,fd,mode):
        require(fd==14 and mode==0o755)
        if self.fail:raise OSError('independent failure after directory creation')
        self.mode=mode
    def fsync(self,fd):self.synced.append(fd)
    def close(self,fd):self.closed.append(fd)


if __name__=='__main__':unittest.main()
