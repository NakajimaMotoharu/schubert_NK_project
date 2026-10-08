"""Read-only final preservation/peer check and ninth sealed native. Diagnostic, not formal."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess

os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
T=R.parents[3]
assert T.name=='pgpt-foundation'
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c'
RUN='PG538-native-nine-diagnostic-v1'
assert subprocess.check_output(['git','diff',SOURCE,'--',':(glob)src/*/src/main/**','src/deployment','pom.xml',':(glob)src/*/pom.xml'],cwd=T)==b''
prior=json.loads((W/'pg531-native-diagnostic-v1.safe.json').read_bytes())
assert prior['productionSource']==SOURCE and prior['eligibleCurrentStreams']==prior['presentStreams']==8
retirement=json.loads((W/'pg537-bootstrap-native-v1.source.json').read_bytes())
assert retirement['actualExit']==0 and (W/'pg537-bootstrap-native-v1.exit').read_text()=='0\n'
assert retirement['privateLogSha256']==hashlib.sha256((W/'pg537-bootstrap-native-v1.private.log').read_bytes()).hexdigest()
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
payload=r'''
import pathlib,hashlib,json,ast,datetime,os,stat,subprocess
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg537-bootstrap-retire-v1')
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
def require(v):
 if not v:raise ValueError('final readonly assertion')
a=ast.parse(raw);names={'command','metadata','strict','tree','show'}
nodes=[n for n in a.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(nodes)==5
nodes += [n for n in a.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in{'UNITS','FIELDS'}for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent sealed final readonly>','exec'))
before_raw=strict(root/'before.private.json',0o600,33554432)
after_raw=strict(root/'after.private.json',0o600,33554432)
assert hashlib.sha256(before_raw).hexdigest()=='62402b7b0b1f1d1d0ec8799652e8ad1a7f6c3a24dedb6b4baac6f29c34eae4db'
assert hashlib.sha256(after_raw).hexdigest()=='c34c058226c43e55b90ce3342a6b21cc74e6137a1a4084daaba7662ad04add59'
before=json.loads(before_raw);after=json.loads(after_raw);assert set(before)==set(after)
assert all(before[k]==after[k]for k in before if k!='credentials')
for name in ('bootstrap-admin-username','bootstrap-admin-password'):
 src=pathlib.Path('/etc/schubert-nk/credentials')/name;target=root/(name+'.retired.private');old=before['credentials'][str(src)]
 assert not os.path.lexists(src) and metadata(target)[:7]==old['metadata'][:7]
 assert hashlib.sha256(strict(target,0o400,256)).hexdigest()==old['sha256']
assert after['credentials']==tree(pathlib.Path('/etc/schubert-nk/credentials'))
for key,path in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage'),('oldProofs','/var/lib/pgpt-s1-preservation/pg526-native-stop-v1'),('bootstrapOldProofs','/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1'),('bootstrapTools','/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1')]:
 assert after[key]==tree(pathlib.Path(path))
assert all(show(u,set(v))==v for u,v in after['units'].items())
assert all(show(u,set(v))==v for u,v in after['configuration'].items())
q="begin isolation level repeatable read read only;set local timezone='UTC';"
for t in after['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
rows={}
for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-v','ON_ERROR_STOP=1','-c',q+'commit;']).splitlines():
 r=json.loads(line);assert r['table']not in rows;rows[r['table']]=r['rows']
assert rows==after['rows']
p=command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"]).splitlines()
assert p==[b'0',b'0']
for name in ('maintenance.lock','startup-admission.lock'):
 s=(pathlib.Path('/run/schubert-nk')/name).lstat()
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)>=8 and f[1]=='FLOCK':
   d=f[5].split(':');assert(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
complete=strict(root/'complete.private',0o600,4096)
assert complete==b'newSyntheticSourcesRetired=true\nallNewScopesReturnedNormally=true\nnormal20Preserved=true\nall24DatabaseUnchanged=true\nunitActions0=true\n'
remote='/run/schubert-nk/pt-coverage/ordinary-bootstrap196/08face250787426aab68796452a0289f.terminal.exec'
v=after['native'][remote];assert v==tree(pathlib.Path('/run/schubert-nk/pt-coverage'))[remote]
assert v['metadata'][2:6]==[999,981,stat.S_IFREG|0o600,1] and 5<=v['metadata'][6]<=16777216
print(json.dumps({'readAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all24Unchanged':True,'batchRows':len(rows['schubert.batch_runs']),
 'nativeFiles':sum(v['sha256']is not None for v in after['native'].values()),'twoSourcesSameInodeRetired':True,
 'peerAdvisoryFlock0':True,'unitsConfigurationOriginalsBackupUnchanged':True,'newStream':{'role':'ordinary-bootstrap196','bytes':v['metadata'][6],'sha256':v['sha256']},
 'proofs':{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in root.iterdir()if not f.name.endswith('.retired.private')}}))
'''
r=subprocess.run(ssh,input=payload.encode(),capture_output=True,timeout=45)
with(W/'pg538-final-readback-v1.private.log').open('xb')as f:f.write(r.stdout);f.write(r.stderr)
assert r.returncode==0 and not r.stderr
final=json.loads(r.stdout);assert final['nativeFiles']==9 and final['peerAdvisoryFlock0']
target=W/'pg538-ordinary-bootstrap196-native-v1.exec';assert not target.exists()
read_payload=r'''
import os,sys,stat,hashlib
p='/run/schubert-nk/pt-coverage/ordinary-bootstrap196/08face250787426aab68796452a0289f.terminal.exec'
fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);s=os.fstat(fd)
assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(999,981,0o600)
def identity(v):return(v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
raw=b''
while True:
 chunk=os.read(fd,65536)
 if not chunk:break
 raw+=chunk;assert len(raw)<=16777216
assert identity(os.fstat(fd))==identity(s);os.close(fd);sys.stdout.buffer.write(raw)
'''
with target.open('xb')as f:
 read=subprocess.run(ssh,input=read_payload.encode(),stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
assert read.returncode==0 and not read.stderr and target.stat().st_size==final['newStream']['bytes']
assert hashlib.sha256(target.read_bytes()).hexdigest()==final['newStream']['sha256']
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
 paths=list(repo.glob(pattern));assert len(paths)==1;cp.append(str(paths[0]))
old_tools=W/'pg531-native-tools-v1';tools=W/'pg538-native-tools-v1';assert not tools.exists();tools.mkdir(mode=0o700)
class_path=str(tools)+':'+str(old_tools)+':'+':'.join(cp)
compile_result=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',class_path,'-d',str(tools),str(R/'NativeStreamInspect538.java'),str(R/'NativeStreamInspect538Test.java')],capture_output=True)
with(W/'pg538-compile-v1.private.log').open('xb')as f:f.write(compile_result.stdout);f.write(compile_result.stderr)
assert compile_result.returncode==0 and compile_result.stdout==compile_result.stderr==b''
test=subprocess.run([str(J/'java'),'-cp',class_path,'NativeStreamInspect538Test'],capture_output=True)
with(W/'pg538-window-oracle-v1.private.log').open('xb')as f:f.write(test.stdout);f.write(test.stderr)
assert test.returncode==0 and test.stderr==b'' and test.stdout.startswith(b'PG538_SESSION_WINDOW_ORACLE independentAssertions=20 ')
modules=['protocol','storage','bootstrap','api','web','batch'];jars=[];native=[]
host=json.loads((T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG495-completion-compound-full-v1/manifest.json').read_bytes())
for module in modules:
 p=W/'pg495-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');row=next(v for v in host['modules']if v['module']==module)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['projectJarSha256'];jars.append(p)
for stream in prior['streams']:
 assert stream['eligibleForCurrentUnion'] and stream['classByteMismatch']==stream['unknownProductionClasses']==0
 p=W/('pg531-'+stream['role']+'-native-v1.exec');assert hashlib.sha256(p.read_bytes()).hexdigest()==stream['sha256'];native.append(p)
result=subprocess.run([str(J/'java'),'-cp',class_path,'NativeStreamInspect538','ordinary-bootstrap196',str(target),*[str(p)for p in jars]],capture_output=True,timeout=30)
with(W/'pg538-bootstrap-inspection-v1.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr)
assert result.returncode==0 and not result.stderr
inspection=json.loads(result.stdout)
assert inspection['singleSession'] and inspection['currentWindowAndRole'] and inspection['classByteMismatch']==inspection['unknownProductionClasses']==0
native.append(target);host_exec=[W/'pg495-host'/m/'jacoco.exec'for m in modules];counters={}
for module,jar in zip(modules,jars):
 result=subprocess.run([str(J/'java'),'-cp',class_path,'NativeCoverage',str(jar),*[str(p)for p in host_exec+native]],capture_output=True,timeout=45)
 with(W/('pg538-'+module+'-counter-v1.private.log')).open('xb')as f:f.write(result.stdout);f.write(result.stderr)
 assert result.returncode==0 and not result.stderr;counters[module]=json.loads(result.stdout)
summary={'run':RUN,'productionSource':SOURCE,'operatorGitHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T).decode().strip(),
         'collectedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'finalIndependentReadback':final,
         'newStream':{**final['newStream'],**inspection},'retirementRun':retirement['run'],'eligibleStreams':9,
         'priorStreamsRetainedSha256':hashlib.sha256((W/'pg531-native-diagnostic-v1.safe.json').read_bytes()).hexdigest(),
         'missingRoles':['ordinary-inspector196'],'counters':counters,'formalAccepted':False,'nativeAllScopeAccepted':False,
         'scopeNote':'Minimum individual provenance only; all mandatory actor/time/negative/source-run matrix and formal100 remain unaccepted.',
         'rawExportedToGit':False,'businessActions':0}
out=W/'pg538-native-nine-diagnostic-v1.safe.json'
with out.open('x')as f:json.dump(summary,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':RUN,'presentStreams':9,'eligibleStreams':9,'newRoleInspection':inspection,
                 'missed':{m:{c:v[c]['missed']for c in ['LINE','METHOD','CLASS','BRANCH']}for m,v in counters.items()},
                 'safeSummarySha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formalAccepted':False}))
