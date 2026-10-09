"""Immutable standalone fixed pending original code-only tool, current750 ABI."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg835_pending_sources as p

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')

def sources():
    result={'Pg835PendingDeployment.java':p.java(),'Pg835PendingDeploymentTest.java':(R/'Pg498PendingDeploymentTest.java').read_text().replace('Pg498PendingDeployment','Pg835PendingDeployment').replace('PG495','PG832').replace('PG498','PG835'),'pg835_pending_refs.py':p.refs(),'pg835_before_freeze.py':p.before_freeze(),'pg835_snapshot.py':p.snapshot_library()}
    for name in ('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):result[name]=(R/name).read_text()
    result['pg777_reference_capability.py']=(W/'pg798-scope-tools-v1/pg777_reference_capability.py').read_text()
    return result

def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert(W/'pg833-current-before832-v1.exit').read_text()=='0\n'
    post=json.loads((W/'pg833-current-before832-v1.safe.json').read_text());assert post['snapshotSha256']=='d725011754d5a06d8591b16820b9e272aa41116723df8d6946384d6d1bc13652'and post['M_A0']and post['databaseClient0']
    subprocess.run(['python3','-B',str(R/'pg835_pending_test.py')],check=True)
    target=W/'pg835-pending-tools-v1';target.mkdir(mode=0o700)
    for old in(W/'pg798-scope-tools-v1').glob('*.class'):
        with(target/old.name).open('xb')as f:f.write(old.read_bytes());os.fchmod(f.fileno(),0o400)
    for name,raw in sources().items():
        if name.endswith('.py'):ast.parse(raw)
        with(target/name).open('x')as f:f.write(raw);os.fchmod(f.fileno(),0o400)
    release=W/'pg796-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(m2/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for phase,args in [('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg835PendingDeployment.java'),str(target/'Pg835PendingDeploymentTest.java')]),('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg835PendingDeploymentTest'])]:
        log=W/('pg835-'+phase+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        with(W/('pg835-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
        if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
    files={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
    for f in target.iterdir():f.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True)
    assert not subprocess.check_output(['git','status','--porcelain'])and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
    safe={'actualExit':0,'operatorSource':head,'productionSource':p.OLD_SOURCE,'candidateSource':p.SOURCE,'manifestSha256':p.DIGEST,'fileHashes':files,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg835-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}))

if __name__=='__main__':main()
