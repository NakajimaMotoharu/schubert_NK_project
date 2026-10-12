"""Frozen failed phase observation while exact retained host gate stays owned.

SSC276 failed-phase readonly diagnosis only; not a second management action.
No Ref/DB lease acquisition, signal, stop, mutation, or force-unlock.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH

HOST_PID=282491
SLOT='pg1805-retained-stop-readonly-diagnosis-v1'


def owner():
    proc=Path('/proc')/str(HOST_PID);raw=(proc/'cmdline').read_bytes()
    if raw.split(b'\0')[-2]!=b'tools/quality/pg1802_warning_owned_stop_dispatch.py'and b'tools/quality/pg1802_warning_owned_stop_dispatch.py\0stop\0'not in raw:raise ValueError('fixed actual failed host required')
    s=(P/'current-management-critical.lock').stat();matches=[]
    for line in Path('/proc/locks').read_text().splitlines():
        f=line.split()
        if len(f)>=8 and f[1]=='FLOCK'and f[5]==f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}':matches.append(f)
    if len(matches)!=1 or matches[0][1:5]!=['FLOCK','ADVISORY','WRITE',str(HOST_PID)]:raise ValueError('sole retained host exclusion required')
    log=(W/'pg1802-stop-v1.private.log').read_bytes()
    if b'PG1800_RUNTIME_RESUME_UNKNOWN phase=REFERENCE_SCOPE 'not in log or (W/'pg1802-stop-v1.exit').exists():raise ValueError('same fixed retained failure required')
    return {'pid':HOST_PID,'ticks':int((proc/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(raw).hexdigest(),'gate':[s.st_dev,s.st_ino],'failureLogSha256':hashlib.sha256(log).hexdigest()}


PAYLOAD=r'''
import hashlib,json,pathlib,re
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1800-native-stop-v1')
log=(root/'refs-prepare.private.log').read_bytes()
frames=[]
for line in log.decode('utf-8').splitlines():
 m=re.fullmatch(r'  File "([^"]+)", line ([0-9]+), in ([A-Za-z0-9_<>]+)',line)
 if m:frames.append({'file':pathlib.Path(m[1]).name,'line':int(m[2]),'function':m[3]})
actors=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:raw=(p/'cmdline').read_bytes()
 except FileNotFoundError:continue
 if b'Pg1800NativeStop\x00stop\x00'in raw or b'/pg1800_native_refs.py\x00stop\x00'in raw:
  st=(p/'stat').read_text().rpartition(')')[2].split()
  actors.append({'pid':int(p.name),'ticks':int(st[19]),'ppid':int(st[1]),'argvSha256':hashlib.sha256(raw).hexdigest(),'fdCount':len(list((p/'fd').iterdir()))})
names=sorted(p.name for p in root.iterdir());assert not any('term-once'in n or 'stop-once'in n for n in names)
print(json.dumps({'actualExit':0,'frames':frames,'logSha256':hashlib.sha256(log).hexdigest(),'actors':actors,'privateFileNames':names,'signalsStopsSqlWrites0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    after=owner()
    if before!=after:raise ValueError('retained owner/failure changed during diagnosed readonly observation')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
