"""PG500/N11 persistent hash/metadata and Unit declaration audit; no state mutation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.umask(0o077)
private = Path('/home/mini/codex/project1/work/pgpt-vm/private')
options = ['-i', str(private/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(private/'known_hosts'),
           '-p','22222','ubuntu@127.0.0.1']
payload = r'''
import hashlib,json,os,pathlib,stat,subprocess
assert os.geteuid()==0
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly/refs-after.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3'
baseline=json.loads(raw)
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
def metadata(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(root):
 result={}
 for p in [root,*sorted(root.rglob('*'))]:
  m=metadata(p);digest=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  assert m==metadata(p);result[str(p)]={'metadata':m,'sha256':digest}
 return result
preserved={};lost=[];different=[]
for name,expected in baseline['trees'].items():
 if name.startswith('/run/'):
  p=pathlib.Path(name);assert not p.exists();lost.append(name)
 else:
  actual=tree(pathlib.Path(name));assert actual==tree(pathlib.Path(name))
  if actual!=expected:different.append(name)
  preserved[name]=actual
record={'persistentTrees':preserved,'differences':different,'oldVolatileTreesAbsent':lost,
 'lockMetadata':{n:metadata(pathlib.Path('/run/schubert-nk')/n) for n in ['maintenance.lock','startup-admission.lock']},
 'releaseFileStore':subprocess.check_output(['/usr/bin/findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG495','--output','OPTIONS','--noheadings']).decode().strip(),
 'runtimePresent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists()}
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg500-cold-readonly/persistent.private.json')
with out.open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'persistentRoots':len(preserved),'persistentEntries':sum(len(v) for v in preserved.values()),
 'differences':different,'volatileAbsent':len(lost),'currentBoot':'cc9ed874-7f4f-450e-a188-8de1e42c8441',
 'releaseHostReadOnly':record['releaseFileStore'].split(',')[0]=='ro','runtimePresent':record['runtimePresent'],
 'starts':0,'databaseUpdates':0,'oldRetirementProven':False}))
assert not different
'''
log=Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg500-persistent-readonly-v1.private.log')
assert not log.exists()
with log.open('xb') as handle:
    result=subprocess.run(['ssh',*options,'sudo -n python3 -B -'],input=payload.encode(),
                          stdout=handle,stderr=handle,timeout=120)
if result.returncode==0:
    print(log.read_text().strip())
else:
    print(json.dumps({'result':'NOT_ACCEPTED','exitCode':result.returncode,
                      'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}))
raise SystemExit(result.returncode)
