"""Exact current fixed failed phase; structured private codes only, observation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH

HOST_PID=288085
SLOT='pg1820-identity-stop-retained-diagnosis-v1'


def owner():
    p=Path('/proc')/str(HOST_PID);argv=(p/'cmdline').read_bytes()
    if b'tools/quality/pg1816_identity_warning_owned_stop_dispatch.py\0stop\0'not in argv:raise ValueError('actual retained fixed host required')
    gate=(P/'current-management-critical.lock').stat();matches=[]
    for line in Path('/proc/locks').read_text().splitlines():
        f=line.split()
        if len(f)>=8 and f[1]=='FLOCK'and f[5]==f'{os.major(gate.st_dev):02x}:{os.minor(gate.st_dev):02x}:{gate.st_ino}':matches.append(f)
    if len(matches)!=1 or matches[0][1:5]!=['FLOCK','ADVISORY','WRITE',str(HOST_PID)]:raise ValueError('actual sole same host gate required')
    log=(W/'pg1816-stop-v1.private.log').read_bytes()
    if b'PG1808_RUNTIME_RESUME_UNKNOWN phase=REFERENCE_SCOPE 'not in log or (W/'pg1816-stop-v1.exit').exists():raise ValueError('same retained failed phase required')
    return {'pid':HOST_PID,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'gate':[gate.st_dev,gate.st_ino],'failureLogSha256':hashlib.sha256(log).hexdigest()}


PAYLOAD=r'''
import hashlib,json,pathlib,re
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1808-native-stop-v1');raw=(root/'refs-prepare.private.log').read_bytes();lines=[]
for line in raw.decode().splitlines():
 if re.fullmatch(r'PG1808_(?:READBACK_UNKNOWN type=[A-Za-z_]+|FRAME method=[A-Za-z0-9_<>]+ line=[0-9]+)',line):lines.append(line)
assert lines
actors=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:argv=(p/'cmdline').read_bytes();args=argv.split(b'\0')
 except FileNotFoundError:continue
 if args[0]not in[b'/opt/jdk-25.0.4/bin/java',b'/usr/bin/python3']:continue
 if b'Pg1808NativeStop'in args or b'/var/lib/pgpt-s1-preservation/pg1808-warning-owned-stop-tools-v1/pg1808_native_refs.py'in args:
  s=(p/'stat').read_text().rpartition(')')[2].split()
  actors.append({'pid':int(p.name),'ticks':int(s[19]),'ppid':int(s[1]),'argvSha256':hashlib.sha256(argv).hexdigest(),'fdCount':len(list((p/'fd').iterdir())),'backendPid':int(args[-2])if args[0]==b'/usr/bin/python3'else None})
names=sorted(p.name for p in root.iterdir());assert not any('term-once'in n or 'stop-once'in n for n in names)
print(json.dumps({'actualExit':0,'structuredTrace':lines,'logSha256':hashlib.sha256(raw).hexdigest(),'actors':actors,'privateFileNames':names,'signalsStopsSqlWrites0':True,'rawExported':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('retained host/phase changed')
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'hostRetainedOwner':before,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
