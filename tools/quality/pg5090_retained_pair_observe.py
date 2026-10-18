"""BUG1405 failed-phase read-only discovery; never a signal/close permission."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, SSH
from pg4996_resume_connection import authenticate_host

SLOT = 'pg5090-retained-pair-observe-v1'
BODY = r'''
import hashlib,json,os,pathlib,stat,subprocess,dbus
def require(value):
 if not value:raise ValueError('fixed failed phase discovery refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
def metadata(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def actor(pid):
 p=pathlib.Path('/proc')/str(pid);status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 return {'pid':pid,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'exe':os.readlink(p/'exe'),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'authority':{k:status[k].strip()for k in ['Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid']},'cgroup':(p/'cgroup').read_text(),'children':sorted({int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}),'fds':{f.name:{'metadata':metadata(f.stat()),'target':os.readlink(f),'fdinfo':(p/'fdinfo'/f.name).read_text()}for f in(p/'fd').iterdir()}}
left=actor(927504);right=actor(927536)
require(left['ticks']==31055084 and left['argvSha256']=='8bfbbbf082fadbc9569bbc0f2d21980d9eb02a03f1215594f983b5b79e6dc0bc' and left['children']==[927536])
require(right['authority']['PPid']=='927504' and right['children']==[])
bus=dbus.SystemBus(private=True)
try:
 d=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');names=[]
 for name in d.ListNames():
  if not str(name).startswith(':'):continue
  try:pid=int(d.GetConnectionUnixProcessID(name))
  except dbus.DBusException:continue
  if pid==927536:names.append(str(name))
 require(len(names)==1)
finally:bus.close()
q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],capture_output=True,timeout=10);require(r.returncode==0 and not r.stderr and r.stdout.splitlines()==[b'0',b'0'])
require(left==actor(927504)and right==actor(927536))
print(json.dumps({'actualExit':0,'parent':left,'child':right,'childBusNames':names,'serverPeerAdvisory0':True,'signals0':True,'oldCloseUnknown':True}))
'''


def main():
    authenticate_host()
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = BODY.encode()
    (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw, capture_output=True, timeout=45)
    for name, blob in [('stdout.private.json', r.stdout), ('stderr.private.log', r.stderr)]:
        with (out / name).open('xb') as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(),
             'stdoutSha256': hashlib.sha256(r.stdout).hexdigest(), 'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'signals0': True, 'discoveryNotPermission': True, 'formalAccepted': False}
    if r.returncode == 0:
        v = json.loads(r.stdout)
        value.update(parentPid=v['parent']['pid'], parentTicks=v['parent']['ticks'], childPid=v['child']['pid'],
                     childTicks=v['child']['ticks'], parentFdCount=len(v['parent']['fds']), childFdCount=len(v['child']['fds']),
                     childArgvSha256=v['child']['argvSha256'], serverPeerAdvisory0=v['serverPeerAdvisory0'])
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
