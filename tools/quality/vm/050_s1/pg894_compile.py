"""Current862 full ABI/Werror; fresh895 only, new-only immutable Bootstrap profile."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg894_bootstrap_sources import files,SOURCE
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg895-bootstrap-before-v1.exit').read_bytes()==b'0\n'
 before=json.loads((W/'pg895-bootstrap-before-v1.safe.json').read_bytes());assert before['actualExit']==0 and before['productionSource']==SOURCE
 subprocess.run(['python3','-B',str(R/'pg894_source_test.py')],check=True)
 raw=files(before['beforeSha256']);old=W/'pg864-completed-tools-v3';frozen=json.loads((W/'pg864-frozen-v3.safe.json').read_bytes());assert frozen['actualExit']==0
 target=W/'pg894-bootstrap-tools-v1';target.mkdir(mode=0o700)
 for name,digest in frozen['fileHashes'].items():
  p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
  if name.endswith('.class'):
   with(target/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(p.read_bytes())
 for name,value in raw.items():
  if name.endswith('.py'):ast.parse(value)
  with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(value)
 release=W/'pg862-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(repo/x)for x in('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for phase,args in [('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg894BootstrapExisting.java'),str(target/'Pg894BootstrapArgumentTest.java')]),('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg894BootstrapArgumentTest'])]:
  log=W/('pg894-'+phase+'-v1.private.log')
  with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  with(W/('pg894-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
  if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
 for p in target.iterdir():p.chmod(0o400)
 with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(hashes,f,sort_keys=True)
 assert subprocess.check_output(['git','status','--porcelain'])==b''and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
 safe={'actualExit':0,'productionSource':SOURCE,'operatorSource':head,'beforeSha256':before['beforeSha256'],'fileHashes':hashes,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
 with(W/'pg894-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}))
if __name__=='__main__':main()
