"""Fresh readonly full post plus retained current first Inspector provenance; no fixture/start."""
import ast
from pathlib import Path
from pg901_bootstrap_post_v3 import payload as previous
R=Path(__file__).resolve().parent
INSPECTOR='''
first_raw=strict(base/'pg875-completed-readonly-v1/before.private.json',0o600,33554432)
require(hashlib.sha256(first_raw).hexdigest()=='b5d1dd652da7613a789f102e259237b8cb7e90d25c89f6a007c7c24d80f5fe38')
first=json.loads(first_raw)
old_raw=strict(base/'pg870-ordinary-before-v1/after.private.json',0o600,33554432);old=json.loads(old_raw)
require(first['rows']==old['rows'])
run='19022204-8a9e-418d-ba2a-9967ff923dc2';cutoff='2026-10-09T18:28:14.612111+00:00';inv='244830fc431344e18738750cdbfe0fa9'
progress=[v for v in value['rows']['schubert.inbox_inspection_progress']if v['run_id']==run]
require(len(progress)==1 and progress[0]['cutoff']==cutoff and all(progress[0][k]==0 for k in ('inspected_count','deleted_count','protected_count'))and progress[0]['completed_at']is not None)
require(not any(v['run_id']==run for v in old['rows']['schubert.inbox_inspection_progress']))
steps=[v for v in value['rows']['schubert.batch_runs']if v['run_id']==run and v['step']=='CLEAN_INBOX_OUTBOX']
require(len(steps)==1 and steps[0]['status']=='SUCCESS'and steps[0]['failure_count']==0 and steps[0]['error_code']is None)
journal=command(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-inbox-inspector.service','INVOCATION_ID='+inv,'-o','json','--no-pager'])
records=[json.loads(l)for l in journal.splitlines()]
require(all(v.get('_BOOT_ID')=='cc9ed8747f4f450ea1888de1e42c8441'and v.get('_PID')=='1'and v.get('_UID')=='0'and v.get('INVOCATION_ID')==inv for v in records))
def single(mid,kind,job,result):
 v=[v for v in records if v.get('MESSAGE_ID')==mid and v.get('JOB_TYPE')==kind and v.get('JOB_ID')==job]
 require(len(v)==1 and (result is None or v[0].get('JOB_RESULT')==result));return v[0]
start=single('7d4958e842da4a758f6c1cdc7b36dcc5','start','189749',None)
done=single('39f53479d3a045ac8e11786248231fbf','start','189749','done')
stop=single('9d1aaa27d60140bd96365438aad20286','stop','189896','done')
require(183192933299<int(start['__MONOTONIC_TIMESTAMP'])<int(done['__MONOTONIC_TIMESTAMP'])<int(stop['__MONOTONIC_TIMESTAMP'])<184317014132)
first_done=strict(pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d.done'),0o600,141)
require(first_done==b'NKDONE1\\n19022204-8a9e-418d-ba2a-9967ff923dc2\\n2026-10-09T18:28:14.612111Z\\ncf07d74f-14c7-4223-9eb9-82eb6f0fbd0d\\n2026-10-09T18:46:44.362279Z\\n0\\n')
import pwd
identity=pwd.getpwnam('schubert-inbox-inspector');files=[]
for suffix,digest in (('terminal.exec','75b4dc1db7e23e0d8e3d552a81f1f9959d95ef87b933f3ec75a30158d36bf17f'),('closing.exec','6f817e054e12c7c93c8bf466dda11e986c97e495b40471004b24867d6a901f4a')):
 p=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-inspector196')/(inv+'.'+suffix);s=p.lstat();name=str(p)
 require(name not in old['coverageBefore']and name in native and metadata(p)==native[name]['metadata'])
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(identity.pw_uid,identity.pw_gid,0o600,1)and hashlib.sha256(p.read_bytes()).hexdigest()==native[name]['sha256']==digest)
 files.append({'relative':str(p.relative_to('/run/schubert-nk/pt-coverage')),'sha256':digest,'bytes':s.st_size})
require(native==snapshot())
result['inspector']={'files':files,'invocationSha256':hashlib.sha256(inv.encode()).hexdigest(),'actualPid1StartJob':'189749','actualPid1StopJob':'189896','parentFirstGenuineRun':'PG875','firstRootProgressNormal':True,'unitLiveExitStatusIndependentlyCaptured':False,'historicalGcIsNotNotRun':True,'journalSha256':hashlib.sha256(journal).hexdigest(),'oldBeforeSha256':hashlib.sha256(old_raw).hexdigest(),'lowerMs':int(start['__REALTIME_TIMESTAMP'])//1000-1000,'upperMs':int(stop['__REALTIME_TIMESTAMP'])//1000+1000}
'''
def payload(proof,seals):
 raw=previous(proof,seals).replace('pg901-bootstrap-post-v3','pg906-retained-inspector-v1').replace('PG901-bootstrap-post-v3','PG906-retained-inspector-v1')
 marker="with(save/'result.safe.json').open('x')as f:";assert raw.count(marker)==1
 # snapshot() borrows Ref scope; perform stable-native check BEFORE finally releases references.
 extra=INSPECTOR.replace('require(native==snapshot())','require(native==tree(pathlib.Path(\'/run/schubert-nk/pt-coverage\')))')
 raw=raw.replace(marker,extra+'\n'+marker);ast.parse(raw);return raw
if __name__=='__main__':
 source=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg906_retained_inspector.py'),'__name__':'retained_inspector'}
 exec(compile(source,'<901 readonly dispatcher>','exec'),env);env['payload']=payload
 main_source=source[source.index('def main():'):source.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg906-retained-inspector-v1')
 exec(compile(main_source,'<906 retained inspector>','exec'),env);env['main']()
