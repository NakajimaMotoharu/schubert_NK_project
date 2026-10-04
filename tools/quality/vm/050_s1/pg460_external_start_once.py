"""PG460 retry of exact signed PG459 candidate after SSC181: durable one-shot guard, external Morning only.

No permit/DDL/direct child start/recovery; a prior guard requires reattachment.
"""
import json, pathlib, subprocess
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import datetime,hashlib,json,os,pathlib,subprocess
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
current=pathlib.Path('/opt/schubert-nk/current')
assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG459')
assert hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311'
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg460-caddy-nss')
assert b'allOwnedScopesReturnedNormally=true' in (save/'complete.private').read_bytes()
units=['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-api.service','schubert-nk-web.service','artemis.service','caddy.service']
for unit in units:
 raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'-p','MainPID','-p','ControlPID','-p','Job','-p','ControlGroup'],text=True)
 d=dict(line.split('=',1) for line in raw.splitlines())
 assert d['MainPID']==d['ControlPID']=='0' and not d['Job']
 if d['ControlGroup']:
  cg=pathlib.Path('/sys/fs/cgroup')/d['ControlGroup'].lstrip('/')
  if cg.exists():
   for p in cg.rglob('cgroup.procs'):assert not p.read_text().strip()
 assert not list(pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs')) or all(not p.read_text().strip() for p in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'))
assert subprocess.check_output(['/usr/bin/id','-G','caddy'],text=True).strip()=='978'
assert len(list(pathlib.Path('/run/schubert-nk/startup').iterdir()))==13 and not any('intent' in p.name for p in pathlib.Path('/run/schubert-nk/startup').iterdir())
guard=save/'external-start-guard.private.json'
fd=os.open(guard,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:
 json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':'PG459','operation':'PG460-NSS-retry','attemptReserved':True,'originalBudgetSeconds':1800,'repeatForbidden':True},stream);stream.flush();os.fsync(stream.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','-p','InvocationID','-p','MainPID','-p','Job','-p','ExecMainStartTimestampMonotonic'],text=True)
d=dict(line.split('=',1) for line in raw.splitlines());d['clientExit']=r.returncode;d['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['clientSuccessIsNotParentSuccess']=True
fd=os.open(save/'external-start-issued.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:json.dump(d,stream);stream.flush();os.fsync(stream.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(d));raise SystemExit(r.returncode)
'''
r=subprocess.run(SSH+['sudo -n /usr/bin/python3 -'],input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG460_EXTERNAL_START_REFUSED actual='+str(r.returncode)+' priorGuardRequiresReattachment=true privateDiagnostics=true')
raise SystemExit(r.returncode)
