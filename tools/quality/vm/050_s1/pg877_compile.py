"""Fixed genuine875 proof; compile whole current862 ABI, new-only immutable payload."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg877_stop_binding import generate,SOURCE
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg875-completed-readonly-v1.exit').read_bytes()==(W/'pg876-chr-a01-native-v1.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg875-completed-readonly-v1.safe.json').read_bytes());generated=generate(proof)
 subprocess.run(['python3','-B',str(R/'pg877_binding_test.py')],check=True)
 frozen=json.loads((W/'pg864-frozen-v3.safe.json').read_bytes());assert frozen['actualExit']==0
 target=W/'pg877-native-tools-v1';target.mkdir(mode=0o700)
 for name,digest in frozen['fileHashes'].items():
  original=W/'pg864-completed-tools-v3'/name
  assert hashlib.sha256(original.read_bytes()).hexdigest()==digest
  if name.endswith('.class'):
   with (target/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(original.read_bytes())
 for name,raw in generated.items():
  if name.endswith('.py'):ast.parse(raw)
  with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
 release=W/'pg862-release-v1'
 cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
 m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
 cp+=':'+':'.join(str(m2/x)for x in('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for phase,args in [('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg877NativeStop.java'),str(target/'Pg877NativeArgumentTest.java')]),('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg877NativeArgumentTest'])]:
  log=W/('pg877-'+phase+'-v1.private.log')
  with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  with(W/('pg877-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
  if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
 files={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
 for f in target.iterdir():f.chmod(0o400)
 with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True)
 assert subprocess.check_output(['git','status','--porcelain'])==b'' and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
 safe={'actualExit':0,'operatorSource':head,'productionSource':SOURCE,'genuineParentBeforeSha256':proof['beforeSha256'],'fileHashes':files,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
 with(W/'pg877-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}))
if __name__=='__main__':main()
