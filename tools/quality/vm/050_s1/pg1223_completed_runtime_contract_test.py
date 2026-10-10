import ast
import copy
import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
import unittest
from unittest.mock import patch
import pg1223_completed_runtime_contract as p

def parse(s):
    if type(s)is not str:return None
    m=re.fullmatch(r'\{ path=([^ ;]+) ; argv\[\]=(.+?) ; ignore_errors=(yes|no) ; start_time=\[([^\]]*)\] ; stop_time=\[([^\]]*)\] ; pid=([0-9]+) ; code=([^ ;]+) ; status=([^ ;]+) \}',s)
    return m.groups()if m else None

def declaration(argv,history=False):
    return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=['+('oldstart'if history else'n/a')+'] ; stop_time=['+('oldend'if history else'n/a')+'] ; pid='+('99'if history else'0')+' ; code='+('exited'if history else'(null)')+' ; status='+('0'if history else'0/0')+' }'

def fixture():
    fm=[11,22,0,0,stat.S_IFREG|0o644,1,647,100,100]
    dm=[11,21,0,0,stat.S_IFDIR|0o755,2,200,100,100]
    cfg={u:{k:'literal-'+k for k in p.FIELDS}for u in [p.MORNING,*['unit'+str(i)for i in range(9)]]}
    for u in cfg:cfg[u]['ExecStart']=declaration('/usr/bin/java -cp fixed Main',True);cfg[u]['ExecStop']=declaration('/usr/bin/java stop',True)
    cfg[p.MORNING]['ExecStart']=declaration('/usr/bin/java -cp fixed Main --resume '+p.RUN,True)
    cfg[p.MORNING]['DropInPaths']='/etc/native.conf '+p.TARGET
    before={'configuration':cfg,'runtime':{p.ROOT:{'metadata':dm,'sha256':None},p.TARGET:{'metadata':fm,'sha256':p.SHA}},'unitFilesActual':{p.TARGET:fm+[p.SHA],'other':[1]},'units':{'ten':'exacthistory'},'rows':{'all24':'encrypted-retained'},'startup':{'epoch':'retained'},'originals':{'done':'exact'},'backup':{'bundle':'retained'},'extraDurable':{'credential':'hashonly'},'pid1':{'genuine':'done'}}
    after=copy.deepcopy(before);after['runtime'].pop(p.TARGET);after['unitFilesActual'].pop(p.TARGET)
    after['runtime'][p.ROOT]['metadata'][6:]=[100,200,200]
    after['configuration'][p.MORNING]['ExecStart']=declaration('/usr/bin/java -cp fixed Main')
    after['configuration'][p.MORNING]['DropInPaths']='/etc/native.conf'
    return before,after

class RuntimeContractTest(unittest.TestCase):
    def test_independent_all_fields_and_history_negative(self):
        b,a=fixture();self.assertTrue(p.same_except_runtime(b,a,parse));checks=0
        for k in a.keys()-{'configuration','runtime','unitFilesActual'}:
            n=copy.deepcopy(a);n[k]=None
            with self.assertRaises(ValueError):p.same_except_runtime(b,n,parse)
            checks+=1
        for u,c in a['configuration'].items():
            for k in p.FIELDS:
                n=copy.deepcopy(a);n['configuration'][u][k]='foreign'
                with self.assertRaises(ValueError):p.same_except_runtime(b,n,parse)
                checks+=1
        n=copy.deepcopy(a);n['configuration']['unit0']['ExecStart']=declaration('/usr/bin/java -cp fixed Main')
        self.assertTrue(p.same_except_runtime(b,n,parse))
        n['configuration']['unit0']['ExecStart']=declaration('/usr/bin/java -cp foreign Main')
        with self.assertRaises(ValueError):p.same_except_runtime(b,n,parse)
        for n in [None,{},dict(a,unitFilesActual={}),dict(a,runtime={})]:
            with self.assertRaises(ValueError):p.same_except_runtime(b,n,parse)
        print('PG1223_LITERAL_ORACLE negativeCases='+str(checks)+' productionExpected0=true')

    def test_actual_disjoint_runtime_and_unit_file_scopes(self):
        b,a=fixture();b['unitFilesActual'].pop(p.TARGET)
        self.assertTrue(p.same_except_runtime(b,a,parse))
        for field in ['unitFilesActual','runtime']:
            n=copy.deepcopy(a);n[field]['foreign']=None
            with self.assertRaises(ValueError):p.same_except_runtime(b,n,parse)
        for field in ['metadata','sha256']:
            n=copy.deepcopy(b);n['runtime'][p.TARGET][field]=[0]*9 if field=='metadata'else'foreign'
            with self.assertRaises(ValueError):p.same_except_runtime(n,a,parse)

    def exercise(self,fault=0,foreign=False,symlink=False):
        events=[];opened=set();native=p.metadata
        class Ops:
            def __getattr__(self,name):
                fun=getattr(os,name)
                if not callable(fun):return fun
                def call(*args,**kw):
                    events.append(name)
                    if len(events)==fault:raise OSError('independent injected IO')
                    value=fun(*args,**kw)
                    if name=='open':opened.add(value)
                    if name=='close':opened.remove(args[0])
                    return value
                return call
        with tempfile.TemporaryDirectory(prefix='pg1223-fd-')as temp:
            root=Path(temp);root.chmod(0o755);golden=b'G'*647;target=root/p.NAME
            if symlink:
                (root/'other').write_bytes(golden);target.symlink_to('other')
            else:target.write_bytes(golden);target.chmod(0o644)
            if foreign:(root/'foreign').write_bytes(b'retained')
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
            def normalized(fd):
                m=native(fd);m[2:4]=[0,0];return m
            expected=normalized(fd)
            tf=os.open(target,os.O_RDONLY);expected_file=normalized(tf)+[hashlib.sha256(golden).hexdigest()];os.close(tf)
            error=None
            try:
                with patch.object(p,'os',Ops()),patch.object(p,'metadata',normalized),patch.object(p,'SHA',hashlib.sha256(golden).hexdigest()):
                    try:p.retire_entry(fd,expected,expected_file)
                    except (ValueError,OSError)as x:error=x
                if error is None:self.assertFalse(target.exists());self.assertFalse(opened)
                if foreign:self.assertEqual((root/'foreign').read_bytes(),b'retained')
                return events,error
            finally:
                for held in opened:os.close(held)
                os.close(fd)

    def test_real_fd_success_all_io_faults_and_foreign(self):
        events,error=self.exercise();self.assertIsNone(error)
        for i in range(1,len(events)+1):
            with self.subTest(operation=events[i-1],position=i):
                _,error=self.exercise(fault=i);self.assertIsInstance(error,OSError)
        for flag in ['foreign','symlink']:
            _,error=self.exercise(**{flag:True});self.assertIsNotNone(error)
        print('PG1223_REAL_FD_ORACLE faultPositions='+str(len(events))+' VM0=true')

if __name__=='__main__':unittest.main()
