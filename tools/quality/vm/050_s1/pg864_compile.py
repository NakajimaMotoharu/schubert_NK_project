"""New-only current832 full ABI/Werror and independent complete generated sources."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg864_completed_sources import sources
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
if __name__=='__main__':
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b'';head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 post=json.loads((W/'pg866-unused862-post-v1.safe.json').read_bytes());assert post['actualExit']==0 and post['actualStageRun']=='PG863-candidate-stage-v6'
 for name in ('pg864_finite_delta_test.py','pg864_namespace_fd_test.py','pg864_source_contract_test.py'):subprocess.run(['python3','-B',str(R/name)],check=True)
 old=W/'pg856-failed-done-tools-v2';frozen=json.loads((W/'pg856-frozen-v3.safe.json').read_bytes());assert frozen['actualExit']==0
 target=W/'pg864-completed-tools-v1';target.mkdir(mode=0o700)
 for name,digest in frozen['fileHashes'].items():
  oldfile=old/name;assert hashlib.sha256(oldfile.read_bytes()).hexdigest()==digest
  if name.endswith('.class'):
   with (target/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(oldfile.read_bytes())
 raw=sources()
 for name,value in raw.items():
  if name.endswith('.py'):ast.parse(value)
  with (target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(value);f.flush();os.fsync(f.fileno())
 release=W/'pg832-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
 m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(m2/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),*[str(target/n)for n in raw if n.endswith('.java')]])]+[(n,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,n])for n in ('Pg864CompletedDeploymentTest','Pg797OwnedDatabaseTest','Pg798DatabaseScopeTest')]
 for phase,args in commands:
  log=W/('pg864-'+phase+'-v1.private.log')
  with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
 files={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
 for f in target.iterdir():f.chmod(0o400)
 with (target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 assert subprocess.check_output(['git','status','--porcelain'])==b''and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
 safe={'run':'PG864-compile-v1','actualExit':0,'operatorSource':head,'installedSource':'2a0d5aa392c85a1dc12a1cdb423978e8500895b8','candidateSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','fileHashes':files,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutation0':True,'formalAccepted':False}
 with (W/'pg864-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({'run':safe['run'],'actualExit':0,'files':len(files),'Werror0':True,'independentOracle0':True,'guestMutation0':True,'formalAccepted':False}))
