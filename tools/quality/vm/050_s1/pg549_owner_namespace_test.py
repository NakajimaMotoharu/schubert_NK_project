"""Actual sealed owner AST with isolated literal proc/locks, both modes; no VM action."""
import ast
import builtins
import copy
import hashlib
import os
from pathlib import Path
import symtable
import tempfile
import types
import unittest

R=Path(__file__).resolve().parent
RAW=(R/'pg480_backup_refs.py').read_text()
assert hashlib.sha256(RAW.encode()).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
NODE=next(n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name=='owner')


class Binding(ast.NodeTransformer):
    def visit_Constant(self,n):
        return ast.copy_location(ast.Constant(b'Pg549CompletedDeployment'),n)if n.value==b'Pg480BackupRecovery'else n


CODE=Binding().visit(copy.deepcopy(NODE));ast.fix_missing_locations(CODE)
TABLE=next(s for s in symtable.symtable(RAW,'sealed-owner','exec').get_children()if s.get_name()=='owner')
FREE={n for n in TABLE.get_identifiers()if TABLE.lookup(n).is_global()}-set(vars(builtins))


class Fixture:
    def __init__(self,mode):
        self.mode=mode;self.cmd=b'/opt/jdk-25.0.4/bin/java\0-x\0Pg549CompletedDeployment\0'+mode.encode()+b'\0'
        self.locks='1: FLOCK ADVISORY WRITE 12345 00:1c:1997 0 EOF\n2: FLOCK ADVISORY WRITE 12345 00:1c:1998 0 EOF\n'
        owner=self
        class FakePath:
            def __init__(self,*parts):self.name='/'.join(map(str,parts)).replace('//','/')
            def __truediv__(self,part):return FakePath(self.name,str(part))
            def __str__(self):return self.name
            def read_bytes(self):
                if self.name=='/proc/12345/cmdline':return owner.cmd
                raise ValueError('unexpected fixture read')
            def read_text(self):
                if self.name=='/proc/12345/stat':return '12345 (java) '+' '.join(['S','1']+['0']*17+['4567'])
                if self.name=='/proc/locks':return owner.locks
                raise ValueError('unexpected fixture read')
            def iterdir(self):
                if self.name=='/proc/12345/fd':return [FakePath(self.name,'10'),FakePath(self.name,'11')]
                raise ValueError('unexpected fixture iteration')
            def readlink(self):
                return FakePath('/run/schubert-nk','maintenance.lock'if self.name.endswith('/10')else'startup-admission.lock')
            def lstat(self):return types.SimpleNamespace(st_dev=os.makedev(0,28),st_ino=1997 if self.name.endswith('/maintenance.lock')else 1998)
        def require(v):
            if not v:raise ValueError('literal owner refused')
        def strict(p,mode,size):
            require(str(p)in('/run/schubert-nk/maintenance.lock','/run/schubert-nk/startup-admission.lock')and mode==0o600 and size==0)
            return b''
        self.env={'pathlib':types.SimpleNamespace(Path=FakePath),'os':types.SimpleNamespace(getppid=lambda:12345,major=os.major,minor=os.minor),'sys':types.SimpleNamespace(argv=['fixture',mode]),'require':require,'strict':strict,'command':lambda *_:None}
        exec(compile(ast.Module(body=[CODE],type_ignores=[]),'<actual sealed owner with isolated proc>','exec'),self.env)


class Test(unittest.TestCase):
    def test_global_contract_and_both_modes(self):
        self.assertEqual(FREE,{'os','pathlib','sys','require','strict'})
        source=(R/'pg549_completed_refs.py').read_text()
        self.assertIn("ownenv={'pathlib':pathlib,'os':os,'sys':sys,'require':require",source)
        for mode in('verify','activate'):
            f=Fixture(mode);self.assertEqual(f.env['owner'](),(12345,4567))
            del f.env['pathlib']
            with self.assertRaises(NameError):f.env['owner']()

    def test_foreign_actor_mode_and_lock(self):
        for mutation in('class','mode','lock','missing'):
            f=Fixture('verify')
            if mutation=='class':f.cmd=f.cmd.replace(b'Pg549CompletedDeployment',b'ForeignJava')
            if mutation=='mode':f.cmd=f.cmd.replace(b'verify',b'activate')
            if mutation=='lock':f.locks=f.locks.replace('WRITE 12345','WRITE 12346')
            if mutation=='missing':f.locks=''
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):f.env['owner']()

    def test_tmpfs_atomic_replacement_directory_and_held_file(self):
        # Only the fixed /run tmpfs profile is claimed; not a cross-filesystem invariant.
        with tempfile.TemporaryDirectory(prefix='pg549-oracle-',dir='/dev/shm')as name:
            p=Path(name);current=p/'epoch.current';current.write_bytes(b'independent old literal\n')
            fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);oldfd=os.open(current,os.O_RDONLY)
            try:
                before=os.fstat(fd);old=os.fstat(oldfd);(p/'epoch.part').write_bytes(b'independent new literal\n');os.replace(p/'epoch.part',current)
                after=os.fstat(fd)
                self.assertEqual((before.st_dev,before.st_ino,before.st_uid,before.st_gid,before.st_mode,before.st_nlink,before.st_size),(after.st_dev,after.st_ino,after.st_uid,after.st_gid,after.st_mode,after.st_nlink,after.st_size))
                self.assertEqual({x.name for x in p.iterdir()},{'epoch.current'})
                self.assertNotEqual(current.stat().st_ino,old.st_ino);self.assertEqual(os.read(oldfd,64),b'independent old literal\n')
            finally:os.close(oldfd);os.close(fd)


if __name__=='__main__':unittest.main()
