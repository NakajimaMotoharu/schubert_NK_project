"""Whole current832 ABI + frozen dependency closure; only after actual846 and A01."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg847_stop_binding import generate
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
def main():
 os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
 assert(W/'pg846-completed-readonly-v1.exit').read_bytes()==b'0\n'and(W/'pg849-chr-a01-native-v1.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg846-completed-readonly-v1.safe.json').read_bytes());generated=generate(proof)
 for test in ('pg847_binding_test.py','pg847_configuration_test.py'):subprocess.run(['python3','-B',str(R/test)],check=True)
 target=W/'pg847-native-tools-v1';target.mkdir(mode=0o700)
 frozen=json.loads((W/'pg841-frozen-v1.safe.json').read_bytes())
 for original in (W/'pg841-resume-tools-v1').glob('*.class'):
  assert hashlib.sha256(original.read_bytes()).hexdigest()==frozen['fileHashes'][original.name]
  with(target/original.name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(original.read_bytes())
 for name,raw in generated.items():
  if name.endswith('.py'):ast.parse(raw)
  with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
 release=W/'pg832-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
 m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
 cp+=':'+':'.join(str(m2/x)for x in('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for phase,args in [('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg847NativeStop.java'),str(target/'Pg847NativeArgumentTest.java')]),('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg847NativeArgumentTest'])]:
  log=W/('pg847-'+phase+'-v1.private.log')
  with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  with(W/('pg847-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
  if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
 files={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
 for f in target.iterdir():f.chmod(0o400)
 with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True)
 assert not subprocess.check_output(['git','status','--porcelain'])and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
 safe={'actualExit':0,'operatorSource':head,'productionSource':proof['productionSource'],'genuineParentBeforeSha256':proof['beforeSha256'],'fileHashes':files,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
 with(W/'pg847-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}))
if __name__=='__main__':main()
