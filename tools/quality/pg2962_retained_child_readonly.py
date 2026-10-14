"""SSC276 single queued recovery: actual child identity/FD proof, no signal."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate
from pg2960_retained_resume_readonly import host_owner

SLOT = 'pg2962-retained-child-readonly-v1'
BODY = r'''
import hashlib,json,os,pathlib,re
os.umask(0o077)
def require(v):
 if not v:raise ValueError('exact current child read-only guard')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg2962-retained-child-readonly-v1'
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'and not os.path.lexists(save))
parent=pathlib.Path('/proc/118988');st=(parent/'stat').read_text().rsplit(')',1)[1].split()
require(int(st[19])==1642675 and hashlib.sha256((parent/'cmdline').read_bytes()).hexdigest()=='74aa0c400f2cce31c86c72fa4b37c41b60bb8230e656c3753e2a32159d6a4b40')
children={int(n)for t in(parent/'task').iterdir()for n in(t/'children').read_text().split()};require(children=={119019})
p=pathlib.Path('/proc/119019');fields=(p/'stat').read_text().rsplit(')',1)[1].split();status=(p/'status').read_text();argv=(p/'cmdline').read_bytes()
require(int(fields[1])==118988 and re.search(r'^Uid:\s+0\s+0\s+0\s+0$',status,re.M)and re.search(r'^Gid:\s+0\s+0\s+0\s+0$',status,re.M))
fds={}
for f in(p/'fd').iterdir():
 s=f.stat();fds[f.name]={'target':os.readlink(f),'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'fdinfo':(p/'fdinfo'/f.name).read_text()}
value={'pid':119019,'ppid':118988,'ticks':int(fields[19]),'argv':argv.decode().split(chr(0)),'argvSha256':hashlib.sha256(argv).hexdigest(),'exe':os.readlink(p/'exe'),'status':status,'cgroup':(p/'cgroup').read_text(),'fds':fds,'signals0':True}
save.mkdir(mode=0o700)
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
for d in[save,base]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'pid':119019,'ppid':118988,'ticks':value['ticks'],'argvSha256':value['argvSha256'],'fdCount':len(fds),'proofSha256':hashlib.sha256((save/'proof.private.json').read_bytes()).hexdigest(),'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    (out / 'payload.private.py').write_text(BODY)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P / 'current-management-critical.lock', validate_owner=host_owner, require_completion=lambda: False):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=BODY.encode(), capture_output=True, timeout=60)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    (out / 'result.private.json').write_bytes(r.stdout)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(BODY.encode()).hexdigest(), 'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'signals0': True, 'formalAccepted': False}
    if not r.returncode:
        value['guest'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
