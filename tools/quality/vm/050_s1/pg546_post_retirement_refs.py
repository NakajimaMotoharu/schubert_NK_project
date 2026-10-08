"""SSC220 fresh readonly admission; no namespace/Unit action. Every acquired scope normal."""
import ast
import hashlib
import json
import os
import pathlib
import stat
import sys
import time
import dbus
from pg543_runtime_readback import load, RUNTIME
from pg543_retirement_contract import require

SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg546-post-retirement-readback-v1')
OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2')


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='readback' and sys.argv[2].isdigit())
    backend=int(sys.argv[2]);require(backend>1);os.umask(0o077)
    raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='owner')
    class FixedOwner(ast.NodeTransformer):
        def visit_Constant(self,n):
            return ast.copy_location(ast.Constant(b'Pg546PostRetirementAdmission'),n)if n.value==b'Pg480BackupRecovery'else n
    node=FixedOwner().visit(node);ast.fix_missing_locations(node)
    boundary_raw=(OLD/'boundaries.private.json').read_bytes()
    require(hashlib.sha256(boundary_raw).hexdigest()=='0e7fe76e884f918d936842d8bf887c03f816099a11a9a988d022720a13c43726')
    boundary=json.loads(boundary_raw)
    env,baseline,snapshot,*_=load(post=True,caddy_before=boundary['caddyExecStartPre'])
    ownenv=dict(globals());ownenv.update({n:env[n]for n in('strict','command')})
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed new post admission owner>','exec'),ownenv)
    held=ownenv['owner']()
    def owner():require(ownenv['owner']()==held)
    env,baseline,snapshot,*_=load(owner,post=True,caddy_before=boundary['caddyExecStartPre'])
    require(env['metadata'](SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and{p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
    oldpins={'runtime-before.private':'3992c3bcbe97066de238cb97678bb71537643bb598dd5b63a702b15d9e2e44e3','boundaries.private.json':'0e7fe76e884f918d936842d8bf887c03f816099a11a9a988d022720a13c43726','refs-prepare.private.log':'a8c3ee7da596b32f5d46a9dd149b485728fcff28633f42c1d00ef562af775120','before.private.json':'c34c058226c43e55b90ce3342a6b21cc74e6137a1a4084daaba7662ad04add59','retire-reserved.private.json':'7f00183f1e5902202a402138e59329e7abf0858a813b42d1da3ead87c99514a9'}
    require({p.name for p in OLD.iterdir()}==set(oldpins))
    for name,sha in oldpins.items():require(hashlib.sha256(env['strict'](OLD/name,0o600,33554432)).hexdigest()==sha)
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    live=True
    def connection():
        identity="a.usename='schubert_batch'and a.application_name='PG546-post-retirement-readback'and a.state='idle in transaction'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted)"if live else'true'
        sql="select count(*)from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk'and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid not in("+str(backend)+",pg_backend_pid());select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==([b'1',b'0',b'1']if live else[b'0',b'0',b'0']))
    savefd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    runtimefd=os.open(RUNTIME.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    original_dirs=[os.fstat(fd)for fd in(savefd,runtimefd)]
    def directories():
        for fd,path,old in zip((savefd,runtimefd),(SAVE,RUNTIME.parent),original_dirs):
            def identity(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink)
            require(identity(path.lstat())==identity(os.fstat(fd))==identity(old)and'system.posix_acl_access'not in os.listxattr(path))
    def save(name,value):
        directories()
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=savefd)
        with os.fdopen(fd,'wb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
        os.fsync(savefd)
    connection();before=snapshot();require(before==snapshot());connection()
    require(before['runtime']is None and all(before[k]==baseline[k]for k in before if k not in('configuration','runtime')))
    save('before.private.json',before);print('REF_READY',flush=True)
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii');require(action in('before','release'));owner();directories()
        if action=='release':live=False
        connection();require(snapshot()==before);connection()
        if action=='release':
            save('after.private.json',snapshot())
            for unit in reversed(refs):manager.UnrefUnit(unit)
            bus.close();os.close(runtimefd);os.close(savefd);print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('new post admission channel ended')


if __name__=='__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG546_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg546_'in frame.filename or'pg543_'in frame.filename:print('PG546_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
