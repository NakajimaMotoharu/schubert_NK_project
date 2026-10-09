"""Independent literal DB/old original bytes oracle for second same-day ALREADY path."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import datetime,hashlib,json,os,pathlib,stat,subprocess
os.umask(0o077);assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
release=pathlib.Path('/opt/schubert-nk/current');assert str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG862'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
base_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg880-ordinary-before-v1/after.private.json').read_bytes();assert hashlib.sha256(base_raw).hexdigest()=='ef5e9a5df932069c7681dbe119cebf26ecf5203bca42cd5002e848e2048f2198';base=json.loads(base_raw)
old=base['rows']['schubert.batch_runs'];assert len(old)==574
run='93cb976e-c36c-47a3-b9e2-0ad28d2996de';prior_run='19022204-8a9e-418d-ba2a-9967ff923dc2'
steps={'CLEAN_BATCH_RUN','CLEAN_EXPIRY','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER'}
def rows():
 q="begin isolation level repeatable read read only;set local timezone='UTC';select coalesce(jsonb_agg(to_jsonb(b)order by id),'[]'::jsonb)from schubert.batch_runs b;commit;"
 p=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],capture_output=True,timeout=15);assert p.returncode==0 and not p.stderr;return json.loads(p.stdout)
def check():
 current=rows();assert len(current)==584
 index={v['id']:v for v in current};assert len(index)==len(current)and all(index[v['id']]==v for v in old)
 added=[v for v in current if v['id']not in {x['id']for x in old}];assert len(added)==10 and all(v['run_id']==run for v in added)
 by_step={v['step']:v for v in added};assert set(by_step)==steps|{'BACKUP_CONFIG','BACKUP_DB'}
 references={v['step']:v for v in old if v['run_id']==prior_run};assert set(references)==set(by_step)and all(v['status']=='SUCCESS'for v in references.values())
 for step in steps:
  v=by_step[step];previous=references[step]
  assert v['status']=='SKIPPED'and v['error_code']=='ALREADY_SUCCESSFUL'and v['error_summary']=='step already successful for business date'
  assert v['target_count']==v['success_count']==v['failure_count']==v['byte_count']==0 and v['started_at']==v['ended_at']
  assert v['business_date']==previous['business_date']=='2026-10-10'and v['attempt']==previous['attempt']+1
 for step,count in [('BACKUP_CONFIG',2),('BACKUP_DB',1)]:
  v=by_step[step];assert v['status']=='SUCCESS'and v['target_count']==v['success_count']==count and v['failure_count']==0 and v['byte_count']>0 and v['error_code']is None and v['error_summary']is None
 return current
first=check();assert first==check()
def metadata(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
old_files=0
for name,expected in base['trees']['/var/lib/schubert-nk/maintenance'].items():
 if not stat.S_ISREG(expected['metadata'][4]):continue
 p=pathlib.Path(name);s=p.lstat();assert metadata(s)==expected['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==expected['sha256']and metadata(p.lstat())==metadata(s);old_files+=1
old_done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d.done').read_bytes()
assert old_done.decode('ascii').splitlines()==['NKDONE1',prior_run,'2026-10-09T18:28:14.612111Z','cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','2026-10-09T18:46:44.362279Z','0']
assert datetime.datetime.fromisoformat('2026-10-09T18:28:14.612111+00:00').astimezone(datetime.timezone(datetime.timedelta(hours=9))).date()==datetime.datetime.fromisoformat('2026-10-09T19:07:23.894279+00:00').astimezone(datetime.timezone(datetime.timedelta(hours=9))).date()
print(json.dumps({'actualExit':0,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','run':run,'priorRun':prior_run,'old574BatchRowsUnchangedTwice':True,'current584BatchRowsStableTwice':True,'eightActualAlreadySkips':True,'skipCounters0NoDuplicateMutation':True,'backupTwoCurrentSuccess':True,'oldOriginalFilesUnchanged':old_files,'oldPriorDoneUnchangedSha256':hashlib.sha256(old_done).hexdigest(),'expectedSource':'Handwritten SS343/SSC240 same-JST-day/ALREADY literal statuses/counters/old880 byte+metadata, no Production expected method','operationAuthority':False,'wholeParentAccepted':False,'formalAccepted':False}))
'''
if __name__=='__main__':
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 base=W/'pg893-already-oracle-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=PAYLOAD.encode(),capture_output=True,timeout=60)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
