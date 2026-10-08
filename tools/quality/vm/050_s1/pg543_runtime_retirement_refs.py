"""SSC198 fresh current-owner, dedicated readonly DB, ten Ref; exactly one runtime unlink."""
import ast
import hashlib
import json
import os
from pathlib import Path
import pathlib
import stat
import sys
import time
import dbus
from pg543_runtime_readback import load, RUNTIME
from pg543_retirement_contract import phase_action, require

SAVE = Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2')
PROBE = Path('/var/lib/pgpt-s1-preservation/pg543-runtime-readonly-v2')


def main():
    require(os.geteuid() == 0 and len(sys.argv) == 3 and sys.argv[1] in ('retire','verify') and sys.argv[2].isdigit())
    readonly = sys.argv[1] == 'verify'; backend = int(sys.argv[2]); require(backend > 1)
    save = PROBE if readonly else SAVE
    os.umask(0o077)
    raw = Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    ownernode = next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name == 'owner')
    class Identity(ast.NodeTransformer):
        def visit_Constant(self,n):
            return ast.copy_location(ast.Constant(b'Pg543RuntimeRetirement'),n) if n.value == b'Pg480BackupRecovery' else n
    ownernode = Identity().visit(ownernode); ast.fix_missing_locations(ownernode)
    env, baseline, snapshot, caddy_pre, expected, files = load()
    ownenv = dict(globals()); ownenv.update(pathlib=pathlib); ownenv.update({n:env[n] for n in ('strict','command')})
    exec(compile(ast.Module(body=[ownernode],type_ignores=[]),'<fixed current M-A owner>','exec'),ownenv)
    held = ownenv['owner']()
    def owner():
        require(ownenv['owner']() == held)
        values = {k:v.strip() for k,v in (l.split(':',1) for l in (Path('/proc')/str(held[0])/'status').read_text().splitlines())}
        require(values['Uid'].split() == ['0']*4 and values['Gid'].split() == ['0']*4)
        return held
    env, baseline, snapshot, caddy_pre, expected, files = load(owner)
    require(env['metadata'](save)[2:6] == [0,0,stat.S_IFDIR|0o700,2] and {p.name for p in save.iterdir()} == {'refs-prepare.private.log'})
    bus = dbus.SystemBus(private=True)
    manager = dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs = []
    for unit in env['UNITS']:
        manager.RefUnit(unit); refs.append(unit)
    live_database = True
    def connection():
        ident = "a.usename='schubert_batch' and a.application_name='PG543-runtime-retirement' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)" if live_database else 'true'
        q = "select count(*)from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk' and "+ident+";select count(*)from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in("+str(backend)+",pg_backend_pid());select count(*)from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines() == ([b'1',b'0',b'1'] if live_database else [b'0',b'0',b'0']))
    savefd = os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    runtimefd = os.open(RUNTIME.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    dirs = [os.fstat(fd) for fd in (savefd,runtimefd)]
    def directory_check():
        for fd,path,old in zip((savefd,runtimefd),(save,RUNTIME.parent),dirs):
            current = path.lstat(); held_dir = os.fstat(fd)
            def identity(v):return (v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink)
            require(identity(current) == identity(held_dir) == identity(old) and 'system.posix_acl_access' not in os.listxattr(path))
    def write(name, raw):
        directory_check()
        fd = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=savefd)
        with os.fdopen(fd,'wb') as f:
            os.fchmod(f.fileno(),0o600); f.write(raw); f.flush(); os.fsync(f.fileno())
        os.fsync(savefd)
    connection(); before = snapshot(); require(before == snapshot() and before == baseline); connection()
    write('before.private.json',json.dumps(before,sort_keys=True).encode())
    write('runtime-before.private',env['strict'](RUNTIME,0o644,4096))
    write('boundaries.private.json',json.dumps({'owner':held,'runtime':before['runtime'],'unitFiles':files,'caddyExecStartPre':caddy_pre,'expectedNoResume':expected},sort_keys=True).encode())
    if not readonly:
        write('retire-reserved.private.json',b'{"unlinkOnce":true,"reloadOnce":true,"starts0":true}\n')
    print('REF_READY',flush=True); state = 'READY'; changed = False
    for line in sys.stdin.buffer:
        action = line.rstrip(b'\n').decode('ascii'); next_state = phase_action(state,action,readonly)
        owner(); directory_check()
        if action == 'release':
            live_database = False
        connection()
        if action == 'removed':
            changed = True
        actual = snapshot(changed)
        if not changed:
            require(actual == before)
        else:
            require(all(actual[k] == before[k] for k in before if k not in ('configuration','runtime')))
        connection()
        if action == 'removed':
            write('after.private.json',json.dumps(actual,sort_keys=True).encode())
        if action == 'release':
            for unit in reversed(refs):manager.UnrefUnit(unit)
            bus.close(); os.close(runtimefd); os.close(savefd)
            print('REF_RELEASED',flush=True); return
        state = next_state; print('REF_CHECKED',flush=True)
    raise ValueError('fresh runtime channel ended early')


if __name__ == '__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True)
        print('PG543_REF_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg543_' in frame.filename:print('PG543_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
