"""Fresh stopped current4856 VM/preservation authentication before candidate7fff; no VM state writes."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import run
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg3428_vm_candidate_preflight_readonly as identity

ROOT=Path(__file__).resolve().parents[2];SLOT='pg3752-current-preservation-readonly-v1'
CURRENT='4856b3fcaeb4cae983d77757a38dc0bf56a693e2';BOM='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'


def payload():
    post=json.loads((W/'pg3668-current-browser-runtime-retirement-post-v1/manifest.safe.json').read_bytes());assert post['actualExit']==0 and post['productionSource']==CURRENT
    initial=identity.GUEST[:identity.GUEST.index('units={}')]
    for a,b in [('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',CURRENT),('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863',BOM),('PG2802','PG3420'),('pg2802-manifest.sig','pg3420-manifest.sig')]:initial=initial.replace(a,b)
    previous=(W/'pg3476-outbox-current-full-seal-v1/payload.private.py').read_text();helpers='\n'.join(ast.get_source_segment(previous,n)for n in ast.parse(previous).body if isinstance(n,ast.FunctionDef)and n.name in {'metadata','tree'});assert helpers.count('def metadata(')==helpers.count('def tree(')==1
    header='import stat\nAFTER_SHA='+repr(post['proofHashes']['after.private.json']['sha256'])+'\n'
    return header+initial+'\n'+helpers+'\n'+BODY


BODY=r'''
def require(value):
 if not value:raise ValueError('fresh immutable-current preservation authentication refused')
base=Path('/var/lib/pgpt-s1-preservation');afterfile=base/'pg3662-native-stop-v1/after.private.json';afterraw=afterfile.read_bytes();require(hashlib.sha256(afterraw).hexdigest()==AFTER_SHA)
expected=json.loads(afterraw);require(len(expected)==11 and len(expected['rows'])==24 and len(expected['units'])==10)
units={}
for name in expected['units']:
 r=subprocess.run(['systemctl','show',name,'--property=LoadState,ActiveState,SubState,MainPID,ControlPID,Job,ControlGroup'],capture_output=True,text=True,timeout=10);require(r.returncode==0);fields=dict(l.split('=',1)for l in r.stdout.splitlines());require(fields['MainPID']==fields['ControlPID']=='0'and fields['Job']=='')
 group=fields['ControlGroup']
 if group:
  c=Path('/sys/fs/cgroup'+group)
  if c.exists():require(not(c/'cgroup.procs').read_text().strip()and not any(p.read_text().strip()for p in c.rglob('cgroup.procs')))
 units[name]=fields
java=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdecimal():continue
 try:
  executable=(proc/'exe').resolve(strict=True)
  if executable.name=='java':java.append(int(proc.name))
 except (FileNotFoundError,ProcessLookupError):pass
require(not java)
for name in ['maintenance.lock','startup-admission.lock']:
 p=Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}';require(not any(len(l.split())>=8 and l.split()[5]==key for l in Path('/proc/locks').read_text().splitlines()))
sql="begin isolation level repeatable read read only;set local statement_timeout='5s';"
for table in expected['rows']:
 require(table.startswith('schubert.')or table.startswith('schubert_web_session.'));sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+="select json_build_object('clients',count(*))from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select json_build_object('advisory',count(*))from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;commit;"
def read_rows():
 r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=40);require(r.returncode==0 and len(r.stdout)<67108864);tables={};meta={}
 for line in r.stdout.splitlines():
  item=json.loads(line)
  if'table'in item:require(item['table']not in tables);tables[item['table']]=item['rows']
  else:meta.update(item)
 require(tables==expected['rows']and meta['clients']==meta['advisory']==0);return tables
first=read_rows()
for field in ['runtime','startup','native']:
 directory={'runtime':'/run/systemd/system','startup':'/run/schubert-nk/startup','native':'/run/schubert-nk/pt-coverage'}[field];require(tree(Path(directory))==expected[field])
require(sum(Path(p).suffix=='.exec'for p in expected['native'])==34)
categories=[('originals',expected['originals']),('backup',expected['backup']),*[('extraDurable.'+k,v)for k,v in expected['extraDurable'].items()]]
for category,items in categories:
 require(type(items)is dict and items)
 for name,item in items.items():
  p=Path(name);require(p.is_absolute()and metadata(p)==item['metadata'])
  if item.get('sha256')is not None:require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not any(p.name.endswith('.start.intent')for p in Path('/run/schubert-nk/startup').iterdir()))
require(read_rows()==first and afterfile.read_bytes()==afterraw and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deployedSource':data['source']['commit'],'BOM':sha,'guestBoot':boot,'afterSha256':AFTER_SHA,'all187ArtifactSignatureVerified':True,'allTenKernelJob0':True,'guestJavaActors':0,'all24TablesEqualTwice':True,'dbClientsAdvisoryMA0':True,'native34Preserved':True,'runtimeStartupNativeExactMetadataAndSha':True,'preservedCategories':{k:len(v)for k,v in categories},'currentOriginalClosedAndNoIntent':True,'stateChangingActions':0,'dbWrites':0,'guestFilesWritten':0,'admissionAuthorityIssued':False,'newCandidateDeployed':False,'oldNativeTransferred':False,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean frozen reader required')
    os.umask(0o077);out=W/SLOT;out.mkdir();local=Path('/proc/20445');forward={'pid':20445,'ticks':int((local/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((local/'cmdline').read_bytes()).hexdigest()};assert forward=={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}
    code,text=run(identity.HOST,timeout=30);assert code==0,'actual expected QEMU identity absent; do not boot/fallback';host=json.loads(text.strip());raw=payload();compile(raw,'<fresh stopped-current readonly>','exec');(out/'payload.private.py').write_text(raw);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stdout.safe.json').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'source':CURRENT,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'host':host,'localForward':forward,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
