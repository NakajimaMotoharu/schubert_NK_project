"""SSC190 ordinary NOARGS fresh-run start; durable one-shot guard, no permits/DDL/child starts."""
import hashlib,json,os,pathlib,subprocess
from pg553_precondition import successful_preflight,SOURCE,DIGEST
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
receipt=json.loads((W/'pg553-preflight-host-v2.success.json').read_bytes())
assert successful_preflight((W/'pg553-preflight-host-v2.exit').read_bytes(),receipt)
assert (W/'pg553-oracle-host-v3.exit').read_bytes()==b'0\n' and (W/'pg554-observer-stage-v1.exit').read_bytes()==b'0\n'
assert (W/'pg540-completion-admission-six-v1.source').read_text().strip()==SOURCE and (W/'pg540-completion-admission-six-v1.exit').read_bytes()==b'0\n'
assert (W/'pg554-parent-observer-v1.started').exists() and not(W/'pg554-parent-observer-v1.exit').exists()
first=json.loads((W/'pg554-parent-watch-private-v1.jsonl').open().readline())
assert first=={'observerPrepared':True,'source':SOURCE,'manifestSha256':DIGEST,'starts0':True}
log=W/'pg554-external-start-v1.private.log';assert not log.exists()
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1']
payload=r'''
import datetime,hashlib,importlib.util,json,os,pathlib,shutil,stat,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
tool=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py')
assert hashlib.sha256(tool.read_bytes()).hexdigest()==PREFLIGHT_SHA
spec=importlib.util.spec_from_file_location('sealed_preflight',tool);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=m.ROOT;raw=(root/'before.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==BEFORE_SHA;before=json.loads(raw)
oracle=json.loads((root/'cleanup-oracle.private.json').read_bytes())
assert oracle['source']==before['source']==SOURCE and oracle['manifestSha256']==before['manifestSha256']==DIGEST
assert oracle['beforeSha256']==BEFORE_SHA and oracle['actualCutoffIndependentCalculationRequired']is True and oracle['varyingCategories']==['web_http_sessions']
assert len(oracle['inboxExpectedDeleted'])==28 and len(oracle['inboxIndependentProof'])==28
now=datetime.datetime.now(datetime.timezone.utc)
assert datetime.datetime.fromisoformat(oracle['bounds']['lower'])<=now<=datetime.datetime.fromisoformat(oracle['bounds']['upper'])
current=pathlib.Path('/opt/schubert-nk/current');manifest=(current/'RELEASE-MANIFEST.json').read_bytes()
assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548') and hashlib.sha256(manifest).hexdigest()==DIGEST and json.loads(manifest)['source']['commit']==SOURCE
assert m.stopped()==before['units'];_,rows=m.snapshot();assert rows==before['rows']
for name,physical in [('backup','/srv/schubert-nk/backup'),('original','/var/lib/schubert-nk/maintenance'),('transfer','/srv/schubert-nk/data/transfer'),('startup','/run/schubert-nk/startup')]:assert m.tree(pathlib.Path(physical))==before[name]
assert not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists()
execstart=m.command(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=ExecStart']).decode()
assert 'dev.codex.schubert.nk.batch.file.MorningProcessMain' in execstart and '--resume' not in execstart
for name in ['backup-request','cleanup-request','expiry-request']:assert not list(pathlib.Path('/run/schubert-nk',name).iterdir())
for line in pathlib.Path('/proc/locks').read_text().splitlines():
 parts=line.split()
 if len(parts)>=8 and parts[1]=='FLOCK':
  dev=parts[5].split(':')
  for name in ['maintenance.lock','startup-admission.lock']:
   s=pathlib.Path('/run/schubert-nk',name).lstat();assert (int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg554-external-newrun-v1');assert not save.exists();save.mkdir(mode=0o700)
shutil.copytree('/run/schubert-nk/pt-coverage',save/'native-before',symlinks=False)
for p in [save/'native-before',*(save/'native-before').rglob('*')]:
 assert not p.is_symlink()
 if p.is_dir():os.chmod(p,0o700)
 else:
  assert stat.S_ISREG(p.lstat().st_mode);os.chmod(p,0o600)
  with p.open('rb')as f:os.fsync(f.fileno())
def persist(name,value):
 fd=os.open(save/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
assert m.stopped()==before['units']
now=datetime.datetime.now(datetime.timezone.utc);assert now<=datetime.datetime.fromisoformat(oracle['bounds']['upper'])
persist('external-start-guard.private.json',{'at':now.isoformat(),'source':SOURCE,'manifestSha256':DIGEST,'ordinaryNoargs':True,'beforeSha256':BEFORE_SHA,'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5)
actual=dict(x.split('=',1)for x in raw.splitlines());actual.update(clientExit=r.returncode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientSuccessIsNotParentSuccess=True)
persist('external-start-issued.private.json',actual);print(json.dumps(actual));raise SystemExit(r.returncode)
'''
preflight=pathlib.Path(__file__).with_name('pg553_newrun_preflight.py')
prefix='SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\nBEFORE_SHA='+repr(receipt['beforeSha256'])+'\nPREFLIGHT_SHA='+repr(hashlib.sha256(preflight.read_bytes()).hexdigest())+'\n'
with log.open('xb')as f:
 result=subprocess.run(ssh+['sudo -n python3 -B -'],input=(prefix+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/'pg554-external-start-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'clientSuccessIsNotParentSuccess':True,'reattachOnAnyExistingReservation':True}));raise SystemExit(result.returncode)
