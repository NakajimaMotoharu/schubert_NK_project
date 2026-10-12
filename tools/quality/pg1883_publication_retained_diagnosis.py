"""Fresh actual retained publication owner/FD inventory, no mutation or close inference."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH

HOST_PID=314407
SLOT='pg1883-publication-retained-diagnosis-v1'


def owner():
    p=Path('/proc')/str(HOST_PID);argv=(p/'cmdline').read_bytes()
    if b'tools/quality/pg1880_warning_publication_dispatch.py\0activate\0'not in argv:raise ValueError('current retained publication actor required')
    gate=(P/'current-management-critical.lock').stat();matches=[]
    for line in Path('/proc/locks').read_text().splitlines():
        f=line.split()
        if len(f)>=8 and f[1]=='FLOCK'and f[5]==f'{os.major(gate.st_dev):02x}:{os.minor(gate.st_dev):02x}:{gate.st_ino}':matches.append(f)
    if len(matches)!=1 or matches[0][1:5]!=['FLOCK','ADVISORY','WRITE',str(HOST_PID)]:raise ValueError('current sole retained host gate required')
    log=(W/'pg1880-activate-v1.private.log').read_bytes()
    if b'PG1877_RUNTIME_RESUME_UNKNOWN phase=REFERENCE_SCOPE 'not in log or(W/'pg1880-activate-v1.exit').exists():raise ValueError('current retained phase required')
    return {'pid':HOST_PID,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'gate':[gate.st_dev,gate.st_ino],'failureLogSha256':hashlib.sha256(log).hexdigest()}


PAYLOAD=r'''
import hashlib,json,pathlib,re
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1881-warning-publication-v1');raw=(root/'refs-prepare.private.log').read_bytes()
lines=[s for s in raw.decode('ascii').splitlines()if re.fullmatch(r'PG1877_(?:READBACK_UNKNOWN type=[A-Za-z_]+|FRAME method=[A-Za-z0-9_<>]+ line=[0-9]+)',s)]
assert lines
actors=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:argv=(p/'cmdline').read_bytes();args=argv.split(b'\0')
 except FileNotFoundError:continue
 if args[0]not in[b'/opt/jdk-25.0.4/bin/java',b'/usr/bin/python3']:continue
 if b'Pg1877OrdinaryPublication'in args or b'/var/lib/pgpt-s1-preservation/pg1877-warning-publication-tools-v1/pg1877_native_refs.py'in args:
  s=(p/'stat').read_text().rpartition(')')[2].split()
  fds={}
  for fd in (p/'fd').iterdir():
   target=str(fd.readlink());fds[fd.name]={'target':target,'fdinfoSha256':hashlib.sha256((p/'fdinfo'/fd.name).read_bytes()).hexdigest()}
  actors.append({'pid':int(p.name),'ticks':int(s[19]),'ppid':int(s[1]),'argvSha256':hashlib.sha256(argv).hexdigest(),'fdCount':len(fds),'fds':fds,'backendPid':int(args[-2])if args[0]==b'/usr/bin/python3'else None})
assert len(actors)==2
names=sorted(p.name for p in root.iterdir());assert names==['refs-prepare.private.log']
print(json.dumps({'actualExit':0,'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'structuredTrace':lines,'logSha256':hashlib.sha256(raw).hexdigest(),'actors':actors,'privateFileNames':names,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink()),'unitSha256':hashlib.sha256(pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service').read_bytes()).hexdigest(),'signalsStopsSqlWrites0':True,'rawExported':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('current retained owner changed')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    if not r.returncode:
        safe={**value,'guest':{k:v for k,v in value['guest'].items()if k!='actors'}}
        safe['guest']['actors']=[{k:v for k,v in a.items()if k!='fds'}for a in value['guest']['actors']]
        print(json.dumps(safe))
    else:print(json.dumps(value))
    return r.returncode


if __name__=='__main__':raise SystemExit(main())
