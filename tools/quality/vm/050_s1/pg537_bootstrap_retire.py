"""SSC216 fresh M-A/readonly DB/tenRefs: only the two admitted PG535 synthetic sources."""
import ast
import hashlib
import json
import os
import pathlib
import re
import stat
import sys
import time
import dbus
from pg535_bootstrap_contract import SOURCES, retire_no_replace
from pg537_bootstrap_gc_readback import load, require
from pg537_bootstrap_gc_contract import unchanged_after_gc

SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg537-bootstrap-retire-v1')
CREDS=pathlib.Path('/etc/schubert-nk/credentials')
HANDOFF=pathlib.Path('/var/lib/pgpt-s1-preservation/pg536-bootstrap-owned-handoff-v1')


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='execute'
            and re.fullmatch('[1-9][0-9]*',sys.argv[2]) is not None)
    backend=int(sys.argv[2]);os.umask(0o077)
    raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    tree=ast.parse(raw);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'owner','strict','metadata'}]
    require(len(nodes)==3)
    class FixedOwner(ast.NodeTransformer):
        def visit_Constant(self,n):
            return ast.copy_location(ast.Constant(b'Pg537BootstrapRetire'),n) if n.value==b'Pg480BackupRecovery' else n
    module=FixedOwner().visit(ast.Module(body=nodes,type_ignores=[]));ast.fix_missing_locations(module)
    scope=dict(globals());exec(compile(module,'<frozen fresh owner>','exec'),scope)
    owner=scope['owner'];strict=scope['strict'];metadata=scope['metadata']
    require(metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2]
            and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
    require(hashlib.sha256(strict(HANDOFF/'complete.private.json',0o600,4096)).hexdigest()=='03ebd13e9b28a67222d60eeee03ce42bcc6c002a90ddd44c728ed937c381c3e9')
    preserved=strict(HANDOFF/'after.private.json',0o600,33554432)
    require(hashlib.sha256(preserved).hexdigest()=='aa8f92166b01b23a7ffd0fa56474fae0048ce20a544f90a3ec06b211732e37ad')
    expected=json.loads(preserved)
    env,snapshot=load(owner)
    live_database=True
    def connection(present):
        require(present is False)
        identity="a.usename='schubert_batch'and a.application_name='PG537-bootstrap-guard'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.granted)" if live_database else 'true'
        q="select count(*)from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk'and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid not in("+str(backend)+",pg_backend_pid());"
        require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'1'if live_database else b'0',b'0'])
    env['connection']=connection
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for u in env['UNITS']:manager.RefUnit(u);refs.append(u)
    before=snapshot();actor=json.loads((pathlib.Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1')/'actor.private.json').read_bytes())
    require(unchanged_after_gc(expected,before,actor) and before==snapshot())
    def save(name,value):
        with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        d=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
    save('before.private.json',before)
    credsfd=os.open(CREDS,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    savefd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    held_dirs=[os.fstat(f) for f in (credsfd,savefd)]
    synthetic={name:bytearray(strict(CREDS/name,0o400,256)) for name in SOURCES}
    print('REF_READY',flush=True);state='READY'
    for line in sys.stdin.buffer:
        require(owner()==env['held'])
        for fd,p,prior in zip((credsfd,savefd),(CREDS,SAVE),held_dirs):
            now=p.lstat();held=os.fstat(fd)
            require((now.st_dev,now.st_ino,now.st_uid,now.st_gid,now.st_mode,now.st_nlink)==(held.st_dev,held.st_ino,held.st_uid,held.st_gid,held.st_mode,held.st_nlink)==(prior.st_dev,prior.st_ino,prior.st_uid,prior.st_gid,prior.st_mode,prior.st_nlink))
        action=line.rstrip(b'\n').decode('ascii')
        if action=='retire':
            require(state=='READY' and snapshot()==before)
            save('retire-reserved.private.json',{'twoSyntheticSourcesOnly':True,'unitActions0':True})
            for name,value in sorted(synthetic.items()):
                prior=before['credentials'][str(CREDS/name)]['metadata']
                require(strict(CREDS/name,0o400,256)==value and metadata(CREDS/name)==prior)
                retire_no_replace(credsfd,name,savefd)
                target=SAVE/(name+'.retired.private')
                require(strict(target,0o400,256)==value and metadata(target)[:7]==prior[:7]
                        and not os.path.lexists(CREDS/name))
            os.fsync(credsfd);os.fsync(savefd);env['prepared'].clear()
            after=snapshot();require({k:v for k,v in after.items()if k!='credentials'}=={k:v for k,v in before.items()if k!='credentials'})
            require(after==snapshot());save('after.private.json',after);state='RETIRED';print('REF_CHECKED',flush=True)
        elif action=='release':
            require(state=='RETIRED');live_database=False
            snapshot()
            for u in reversed(refs):manager.UnrefUnit(u)
            bus.close();os.close(credsfd);os.close(savefd)
            for value in synthetic.values():value[:]=b'\0'*len(value)
            print('REF_RELEASED',flush=True);return
        else:raise ValueError('fixed two-source retirement phase required')
    raise ValueError('fresh retirement channel ended')


if __name__=='__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG537_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg537_' in frame.filename or 'pg536_' in frame.filename:print('PG537_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
