"""One durable ordinary noargs start after fresh observer and private before capture."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg870_ordinary_before import payload as prior
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
BODY='''
before_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1/after.private.json').read_bytes();assert hashlib.sha256(before_raw).hexdigest()=='a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980'
before=json.loads(before_raw)
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg872-ordinary-once-v1');assert not os.path.lexists(save)
def persist(name,value):
 with(save/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
with StageReferences():
 resources();limited=protected();assert limited==protected();assert standard_snapshot(limited)==before==standard_snapshot(protected());resources()
 assert before['ordinaryNoargs'] and before['oldOriginalCompleted'] and not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()
 save.mkdir(mode=0o700)
 import shutil
 native=pathlib.Path('/run/schubert-nk/pt-coverage');shutil.copytree(native,save/'native-before',symlinks=False)
 for p in(save/'native-before',*(save/'native-before').rglob('*')):
  assert not p.is_symlink()
  if p.is_dir():os.chmod(p,0o700)
  elif p.is_file():
   os.chmod(p,0o600)
   with p.open('rb')as f:os.fsync(f.fileno())
  else:raise ValueError('private native entry refused')
 assert standard_snapshot(protected())==before;resources()
 persist('external-start-guard.private.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'e01612fcd7f2752df5ae0836b78538fd5e87f120','manifestSha256':'20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','beforeSha256':hashlib.sha256(before_raw).hexdigest(),'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
 r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
 raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5)
 values=dict(line.split('=',1)for line in raw.splitlines());values.update(clientExit=r.returncode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientSuccessIsNotParentSuccess=True,ordinaryNoargs=True,oldCompletedRunNotResumed=True)
 persist('external-start-issued.private.json',values)
print(json.dumps(values));raise SystemExit(r.returncode)
'''
def payload():
    raw=prior();a=raw.index('with StageReferences():');raw=raw[:a]
    old="save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1');assert not os.path.lexists(save)"
    assert raw.count(old)==1;raw=raw.replace(old,'')+BODY
    ast.parse(raw);return raw
if __name__=='__main__':
    os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
    assert json.loads((W/'pg870-ordinary-before-v1.safe.json').read_bytes())['actualExit']==0
    assert (W/'pg871-watch-v1.started').exists()and not(W/'pg871-watch-v1.exit').exists()
    watch=W/'pg871-parent-watch-v1.private.jsonl';assert watch.exists()and watch.stat().st_size>0
    base=W/'pg872-ordinary-once-v1';assert not any(Path(str(base)+s).exists()for s in ('.private.log','.safe.json','.exit'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc)
    with Path(str(base)+'.private.log').open('xb')as f:r=subprocess.run(ssh,input=payload().encode(),stdout=subprocess.PIPE,stderr=f);f.flush();os.fsync(f.fileno())
    safe={'run':'PG872-ordinary-once-v1','actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'formalAccepted':False,'reservationMustBeCheckedBeforeRetry':True}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
