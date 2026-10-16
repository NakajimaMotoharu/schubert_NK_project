"""Read current inspect owner/phase only; never acquire held gates or issue signals."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import SSH, W

GUEST = r'''
import os,json,hashlib,stat,subprocess
from pathlib import Path
assert os.geteuid()==0
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();assert boot=='79a3260a-e16d-42bf-942a-b914ed144c28'
save=Path('/var/lib/pgpt-s1-preservation/pg4448-failed-current-unused-placement-v4-inspect')
actors=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  argv=(p/'cmdline').read_bytes();parts=argv.split(b'\0')
  if not any(x in parts for x in [b'Pg4444UnusedStage',b'/var/lib/pgpt-s1-preservation/pg4444-failed-current-unused-tools-v4/pg4444_native_refs.py']):continue
  fields=(p/'stat').read_text().rsplit(')',1)[1].split()
  actors.append({'pid':int(p.name),'ppid':int(fields[1]),'ticks':int(fields[19]),'state':fields[0],
   'argvSha256':hashlib.sha256(argv).hexdigest(),'fdCount':len(list((p/'fd').iterdir())),'children':(p/'task'/p.name/'children').read_text().split()})
 except(FileNotFoundError,ProcessLookupError):continue
evidence={}
if save.exists():
 for p in save.iterdir():
  s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  raw=p.read_bytes();evidence[p.name]={'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  if p.name=='refs-prepare.private.log':
   assert len(raw)<16384
   evidence[p.name]['diagnostic']=raw.decode('utf-8')
sql="select json_build_object('pid',pid,'role',usename,'application',application_name,'state',state)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=15);assert r.returncode==0
peers=[json.loads(line)for line in r.stdout.splitlines()]
locks=[]
for name in ['maintenance.lock','startup-admission.lock']:
 p=Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
 locks += [line for line in Path('/proc/locks').read_text().splitlines()if len(line.split())>=8 and line.split()[5]==key]
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()=='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
print(json.dumps({'actualExit':0,'boot':boot,'source':json.loads(manifest)['source']['commit'],'actors':actors,'evidence':evidence,'peers':peers,'flocks':locks,
 'candidateReleaseExists':os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG4432'),'candidateSignatureExists':os.path.lexists('/var/lib/pgpt-s1-preservation/pg4432-manifest.sig'),
 'signalsOrBusinessOperations':0,'oldScopesNormal':False,'formalAccepted':False}))
'''


def main():
    if check(GUEST,'<current inspect owner read only>'): raise ValueError('all emitted static0')
    authenticate_host();os.umask(0o077);out=W/'pg4470-inspect-unknown-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(GUEST)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=GUEST.encode(),capture_output=True,timeout=40)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(GUEST.encode()).hexdigest(),'signalsOrBusinessOperations':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
