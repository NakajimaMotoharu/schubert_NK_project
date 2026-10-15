"""Fresh existing VM/current/all-stopped preservation read, no retirement/start authority."""
import ast
import datetime
import hashlib
import json
import inspect
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg3520_outbox_owned_sources_v2 import SOURCE,BOM
import pg3559_preservation_schema_contract as schema

SLOT='pg3556-current-stopped-readonly-v2'


def payload():
    raw=(W/'pg3476-outbox-current-full-seal-v1/payload.private.py').read_text()
    helpers='\n'.join(ast.get_source_segment(raw,n)for n in ast.parse(raw).body
                      if isinstance(n,ast.FunctionDef)and n.name in {'metadata','tree'})
    initial=identity.GUEST[:identity.GUEST.index('units={}')].replace('json,hashlib,os,subprocess,datetime','json,hashlib,os,subprocess')
    for old,new in [('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863',BOM),
                    ('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',SOURCE),('PG2802','PG3420'),('pg2802-manifest.sig','pg3420-manifest.sig')]:initial=initial.replace(old,new)
    post=json.loads((W/'pg3526-outbox-owned-post-v2/manifest.safe.json').read_bytes())
    require=post['actualExit']==0 and post['productionSource']==SOURCE and post['allActorGone']and post['allClientAdvisoryFlock0']
    if not require:raise ValueError('actual current normal stop whole post required')
    catalog=json.loads((W/'pg3530-outbox-current-native-catalog-v1/manifest.safe.json').read_bytes())
    header='import stat,re\nfrom pathlib import PurePosixPath\nCOUNTS='+repr(schema.COUNTS)+'\n'+inspect.getsource(schema.preservation_trees)+'\nAFTER_SHA='+repr(post['proofHashes']['after.private.json']['sha256'])+'\nCATALOG='+repr(catalog)+'\n'
    raw=header+initial+'\n'+helpers+'\n'+BODY
    if check(raw,'<fresh current stopped read-only>'):raise ValueError('complete emitted readonly exports required')
    compile(raw,'<fresh existing current stopped VM>','exec');return raw


BODY=r'''
os.umask(0o077)
def require(value):
 if not value:raise ValueError('fresh current stopped preservation refused')
base=Path('/var/lib/pgpt-s1-preservation');save=base/'pg3556-current-stopped-readonly-v2';require(not os.path.lexists(save))
after_raw=(base/'pg3520-native-stop-v1/after.private.json').read_bytes();require(hashlib.sha256(after_raw).hexdigest()==AFTER_SHA)
expected=json.loads(after_raw);require(len(expected['rows'])==24 and len(expected['units'])==10)
units={}
for name in expected['units']:
 r=subprocess.run(['systemctl','show',name,'--property=LoadState,ActiveState,SubState,MainPID,ControlPID,Job,ControlGroup'],capture_output=True,text=True,timeout=10);require(r.returncode==0)
 fields=dict(l.split('=',1)for l in r.stdout.splitlines());require(fields['MainPID']==fields['ControlPID']=='0'and fields['Job']=='')
 group=fields['ControlGroup']
 if group:
  c=Path('/sys/fs/cgroup'+group)
  if c.exists():require(not(c/'cgroup.procs').read_text().strip()and not any(p.read_text().strip()for p in c.rglob('cgroup.procs')))
 units[name]=fields
for name in ['maintenance.lock','startup-admission.lock']:
 p=Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
 require(not any(len(l.split())>=8 and l.split()[5]==key for l in Path('/proc/locks').read_text().splitlines()))
sql="begin isolation level repeatable read read only;set local statement_timeout='5s';"
for table in expected['rows']:
 require(table.startswith('schubert.')or table.startswith('schubert_web_session.'))
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+="select json_build_object('clients',count(*))from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select json_build_object('advisory',count(*))from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;select json_build_object('serverVersion',current_setting('server_version'));commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=40);require(r.returncode==0 and len(r.stdout)<67108864)
tables={};meta={}
for line in r.stdout.splitlines():
 item=json.loads(line)
 if'table'in item:require(item['table']not in tables);tables[item['table']]=item['rows']
 else:meta.update(item)
require(tables==expected['rows']and meta['clients']==meta['advisory']==0)
runtime=tree(Path('/run/systemd/system'));startup=tree(Path('/run/schubert-nk/startup'))
require(runtime==expected['runtime']and startup==expected['startup'])
for category,items in preservation_trees(expected):
 for path,item in items.items():
  p=Path(path);require(metadata(p)==item['metadata'])
  if item.get('sha256')is not None:require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
native=tree(Path('/run/schubert-nk/pt-coverage'));selected={v['relative']:v for v in CATALOG['selected']}
old=json.loads((base/'pg3464-outbox-current-noargs-once-v1/native-before-manifest.private.json').read_bytes())
physical={str(Path(k).relative_to('/run/schubert-nk/pt-coverage')):v for k,v in native.items()if Path(k).suffix=='.exec'}
require(len(physical)==28 and set(physical)==set(selected)|set(CATALOG['excludedHistorical']))
for relative,item in physical.items():
 if relative in selected:
  require(item['sha256']==selected[relative]['sha256']and item['metadata']==selected[relative]['metadata'])
 else:require(relative in old and item['sha256']==old[relative]['sha256']and item['metadata'][6]==old[relative]['bytes'])
runtime_bodies={k:Path(k).read_text()for k,v in runtime.items()if v['sha256']is not None}
runtime_again=tree(Path('/run/systemd/system'));require(runtime_again==runtime and tree(Path('/run/schubert-nk/startup'))==startup and tree(Path('/run/schubert-nk/pt-coverage'))==native)
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot and manifest.read_bytes()==raw)
save.mkdir(mode=0o700)
private={'source':data['source']['commit'],'BOM':sha,'guestBoot':boot,'units':units,'runtime':runtime,'runtimeBodies':runtime_bodies,'startup':startup,'native':native,'afterSha256':AFTER_SHA,'rowHashes':{k:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()for k,v in tables.items()},'metadata':meta,'actions0':True}
encoded=json.dumps(private,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,base]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'deployedSource':data['source']['commit'],'BOM':sha,'guestBoot':boot,'proofSha256':hashlib.sha256(encoded).hexdigest(),'currentAll187SignatureVerified':True,'allTenKernelJob0':True,'dbClientsAdvisoryMA0':True,'all24RowsEqualStoppedAfter':True,'originalBackupRuntimeStartupPreserved':True,'nativePhysicalFiles':28,'currentSelectedPoints':10,'oldSourceNativeImported':False,'runtimeFilenameHints':[str(Path(k).relative_to('/run/systemd/system'))for k in runtime_bodies if '/zz-'in k],'postgresVersion':meta['serverVersion'],'vmActions':0,'unitActions':0,'dbWrites':0,'admissionAuthorityIssued':False,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed reader required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    local=Path('/proc/20445');forward={'pid':20445,'ticks':int((local/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((local/'cmdline').read_bytes()).hexdigest()}
    if forward!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:raise ValueError('exact current forward generation required')
    code,text=run(identity.HOST,timeout=30)
    if code:raise ValueError('fresh existing QEMU identity refused; no fallback action')
    host=json.loads(text.strip());raw=payload();(out/'payload.private.py').write_text(raw)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    v={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'host':host,'localForward':forward,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'actions0':True,'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
