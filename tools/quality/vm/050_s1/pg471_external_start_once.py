"""PG471 fixed signed candidate, durable one-shot external Morning start only.

No permit/DDL/child start/recovery. A prior reservation requires reattachment.
"""
import json,pathlib,subprocess,re,sys
assert len(sys.argv)==3 and re.fullmatch(r'[0-9a-f]{40}',sys.argv[1]) and re.fullmatch(r'[0-9a-f]{64}',sys.argv[2])
SOURCE=sys.argv[1];DIGEST=sys.argv[2]
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
assert SOURCE==(WORK/'pg471-six-full-v1.source').read_text().strip()
assert (WORK/'pg471-six-full-v1.exit').read_text().strip()=='0'
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import datetime,hashlib,json,os,pathlib,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
current=pathlib.Path('/opt/schubert-nk/current')
assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG471')
assert hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST
assert json.loads((current/'RELEASE-MANIFEST.json').read_bytes())['source']['commit']==SOURCE
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg471-completed-deploy')
assert (save/'complete.private').read_bytes()==b'allOwnedScopesReturnedNormally=true\noriginalDonePreserved=true\nrows361=true\nallBackupPreserved=true\nstarts0=true\npermits0=true\nddl0=true\n'
units=['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-api.service','schubert-nk-web.service','artemis.service','caddy.service']
for unit in units:
 raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'-p','MainPID','-p','ControlPID','-p','Job','-p','ControlGroup','-p','LoadState'],text=True,timeout=5)
 d=dict(line.split('=',1) for line in raw.splitlines())
 assert d['LoadState']=='loaded'
 assert d['MainPID']==d['ControlPID']=='0' and not d['Job']
 if d['ControlGroup']:
  cg=pathlib.Path('/sys/fs/cgroup')/d['ControlGroup'].lstrip('/')
  if cg.exists():
   for p in cg.rglob('cgroup.procs'):assert not p.read_text().strip()
 for p in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'):assert not p.read_text().strip()
assert subprocess.check_output(['/usr/bin/id','-G','caddy'],text=True,timeout=5).strip()=='978'
startup=pathlib.Path('/run/schubert-nk/startup')
assert len(list(startup.iterdir()))==45 and not any('intent' in p.name for p in startup.iterdir())
guard=save/'external-start-guard.private.json'
fd=os.open(guard,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:
 json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':'PG471','source':SOURCE,'manifestSha256':DIGEST,'attemptReserved':True,'originalBudgetSeconds':1800,'repeatForbidden':True},stream);stream.flush();os.fsync(stream.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','-p','InvocationID','-p','MainPID','-p','Job','-p','ExecMainStartTimestampMonotonic'],text=True,timeout=5)
d=dict(line.split('=',1) for line in raw.splitlines());d['clientExit']=r.returncode;d['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['clientSuccessIsNotParentSuccess']=True
fd=os.open(save/'external-start-issued.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:json.dump(d,stream);stream.flush();os.fsync(stream.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(d));raise SystemExit(r.returncode)
'''
r=subprocess.run(SSH+['sudo -n /usr/bin/python3 -B -'],input=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (WORK/'pg471-external-start-v2.private.log').open('xb') as log:log.write(r.stdout);log.write(r.stderr)
print(r.stdout.decode(),end='')
if r.returncode:print('PG471_EXTERNAL_START_REFUSED actual='+str(r.returncode)+' priorGuardRequiresReattachment=true privateDiagnostics=true')
raise SystemExit(r.returncode)
