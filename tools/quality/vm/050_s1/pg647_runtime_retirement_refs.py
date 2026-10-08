"""SSC230 new M/A/same-peer DB/ten-Ref completed retirement witness.

Only the fixed runtime635 file may be removed through the retained real dirFD.
"""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import pathlib
import re
import stat
import subprocess
import sys
import time
import dbus
from pg647_retirement_contract import changed_only, definition, require

BASE = Path('/var/lib/pgpt-s1-preservation')
SAVE = BASE/'pg647-runtime-retirement-v1'
RUNTIME = Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME = 'pg635-once-resume.conf'
TARGET = RUNTIME/NAME


def library():
    raw = (BASE/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    parsed = ast.parse(raw); wanted = {'command', 'metadata', 'strict', 'show', 'tree', 'configuration_fields', 'kernel', 'owner'}
    body = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    constants = [n for n in parsed.body if isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in {'UNITS', 'FIELDS'} for t in n.targets)]
    require(len(body) == 8 and len(constants) == 2)
    class Binding(ast.NodeTransformer):
        def visit_Constant(self, n):
            return ast.copy_location(ast.Constant(b'Pg647RuntimeRetirement'), n) if n.value == b'Pg480BackupRecovery' else n
    module = Binding().visit(ast.Module(body=constants+body, type_ignores=[])); ast.fix_missing_locations(module)
    env = dict(datetime=datetime, hashlib=hashlib, json=json, os=os, pathlib=pathlib, re=re, stat=stat,
               subprocess=subprocess, sys=sys, time=time, require=require)
    exec(compile(module, '<pinned current owner and readonly library>', 'exec'), env)
    return env


def capture_definition(raw):
    tree = ast.parse(raw)
    capture = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'capture')
    value = ast.get_source_segment(raw, capture)
    changes = (
        ("require(v['units']==old['units']and v['configuration']==old['configuration'])", "require(v['units']==old['units'])"),
        ("lines[-2:]==[b'0',b'0']", "lines[-2:]==([b'1',b'1']if live else[b'0',b'0'])"),
        ("require({p.name for p in runtime.iterdir()}=={'pg635-once-resume.conf'})", "require({p.name for p in runtime.iterdir()}==(set()if removed else{'pg635-once-resume.conf'}))"),
        ("v['runtime']=file(runtime/'pg635-once-resume.conf')", "v['runtime']=None if removed else file(runtime/'pg635-once-resume.conf')"),
        ("len(set(paths))==19", "len(set(paths))==(18 if removed else 19)"),
        ("require(v['unitFiles'][str(runtime/'pg635-once-resume.conf')]==v['runtime']);", "require(removed or v['unitFiles'][str(runtime/'pg635-once-resume.conf')]==v['runtime']);"),
        ("d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))", "d=f[5].split(':')\n     if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):require(f[1:5]==['FLOCK','ADVISORY','WRITE',str(held[0])])"),
        ('def capture():', 'def captured():\n  owner();directories();connection()'),
    )
    for old, new in changes:
        require(value.count(old) == 1); value = value.replace(old, new)
    return value


def peer_socket(rows, socket_inodes, port):
    require(type(port) is int and 0 < port <= 65535 and type(socket_inodes) is set)
    source = {f'0100007F:{port:04X}', f'0000000000000000FFFF00000100007F:{port:04X}'}
    target = {'0100007F:1538', '0000000000000000FFFF00000100007F:1538'}
    matches = [f for f in rows if len(f) >= 10 and f[1] in source and f[2] in target
               and f[3] == '01' and f[9] in socket_inodes]
    require(len(matches) == 1)
    return True


def directory_identity(s):
    return (s.st_dev, s.st_ino, s.st_uid, s.st_gid, s.st_mode, s.st_nlink)


def directory_witness(path_stat, fd_stat, initial_stat, attributes, runtime):
    require(directory_identity(path_stat) == directory_identity(fd_stat) == directory_identity(initial_stat)
            and not {'system.posix_acl_access', 'system.posix_acl_default'}.intersection(attributes))
    if runtime:
        require((path_stat.st_uid, path_stat.st_gid, path_stat.st_mode, path_stat.st_nlink)
                == (0, 0, stat.S_IFDIR | 0o755, 2))


def main():
    os.umask(0o077)
    require(os.geteuid() == 0 and len(sys.argv) == 3 and sys.argv[1] == 'retire' and sys.argv[2].isdigit())
    backend = int(sys.argv[2]); require(backend > 1 and Path('/proc/sys/kernel/random/boot_id').read_text().strip() == 'cc9ed874-7f4f-450e-a188-8de1e42c8441')
    env = library(); command, metadata, strict = (env[k] for k in ('command', 'metadata', 'strict'))
    held = env['owner']()
    def owner(): require(env['owner']() == held)
    raw = strict(BASE/'pg646-completed-baseline-v1/before.private.json', 0o600, 67108864)
    require(hashlib.sha256(raw).hexdigest() == 'e9c9b270aea859cc13f69f24bee4406c401a61786b3081b698f20e9ac82be40c')
    baseline = json.loads(raw); require(len(baseline) == 19)
    old_raw = strict(BASE/'pg642-native-stop-v1/after.private.json', 0o600, 67108864)
    require(hashlib.sha256(old_raw).hexdigest() == '011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c')
    old = json.loads(old_raw)
    raw = strict(Path(__file__).parent/'pg646_completed_baseline.py', 0o400, 65536)
    tree = ast.parse(raw); node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
    capture_code = capture_definition(ast.literal_eval(node.value))
    paths = (SAVE, Path('/run/schubert-nk/startup'), Path('/etc/schubert-nk/release-approval'), RUNTIME)
    fds = [os.open(p, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW) for p in paths]; initial = [os.fstat(fd) for fd in fds]
    def directories():
        for p, fd, s in zip(paths, fds, initial):
            directory_witness(p.lstat(), os.fstat(fd), s, os.listxattr(p), p == RUNTIME)
    directories()
    live = True; removed = False
    def connection():
        sql = "select count(*)from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch'and a.datname='schubert_nk'and a.application_name='PG647-runtime-retirement'and a.state='idle in transaction'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
        require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).strip() == (b'1' if live else b'0'))
        if live:
            q="select client_port from pg_stat_activity where pid="+str(backend)+" and client_addr=inet '127.0.0.1';"
            value=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).strip();require(value.isdigit())
            proc=Path('/proc')/str(held[0]);require((proc/'ns/net').stat().st_ino==Path('/proc/self/ns/net').stat().st_ino)
            sockets=set()
            for fd in(proc/'fd').iterdir():
                try:target=str(fd.readlink())
                except FileNotFoundError:continue
                if target.startswith('socket:[')and target.endswith(']'):sockets.add(target[8:-1])
            records=[]
            for name in('tcp','tcp6'):records.extend(line.split()for line in(proc/'net'/name).read_text().splitlines()[1:])
            peer_socket(records,sockets,int(value));owner()
    def file(p):
        before = metadata(p); data = p.read_bytes(); require(before == metadata(p)); return {'metadata': before, 'sha256': hashlib.sha256(data).hexdigest()}
    scope = dict(env, owner=owner, directories=directories, connection=connection, file=file, old=old,
                 base=BASE, live=live, removed=removed, held=held)
    exec(compile(capture_code, '<pinned readonly capture, fixed retirement effects>', 'exec'), scope)
    def snapshot():
        scope.update(live=live, removed=removed); owner();directories();connection()
        value = scope['captured'](); owner();directories();connection(); return value
    def persist(name, value):
        directories();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fds[0])
        with os.fdopen(fd,'wb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
        os.fsync(fds[0])
    bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
    for u in env['UNITS']:manager.RefUnit(u);refs.append(u)
    before=snapshot();require(before==snapshot()==baseline)
    base_raw=(Path('/opt/schubert-nk/current')/'systemd/schubert-nk-morning-controller.service').read_bytes()
    native=strict(Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf'),0o644,4096)
    dropin=definition(base_raw,native);require(strict(TARGET,0o644,4096)==dropin)
    persist('before.private.json',before);print('REF_READY',flush=True);state='READY'
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii');require(action in ({'before','retire'}if state=='READY'else{'release'}))
        owner();directories()
        if action=='retire':
            require(not removed and snapshot()==before);require(strict(TARGET,0o644,4096)==dropin and file(TARGET)==before['runtime'])
            os.unlink(NAME,dir_fd=fds[3]);os.fsync(fds[3]);require(not os.path.lexists(TARGET))
            command(['/usr/bin/systemctl','daemon-reload'],4096);removed=True;state='CHECKED'
        if action=='release':live=False
        now=snapshot()
        if removed:changed_only(before,now,dropin)
        else:require(now==before)
        if action=='release':
            persist('after.private.json',now)
            for u in reversed(refs):manager.UnrefUnit(u)
            bus.close()
            for fd in reversed(fds):os.close(fd)
            print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('completed retirement owner channel ended')


if __name__ == '__main__':
    try: main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG647_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg647' in frame.filename:print('PG647_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
