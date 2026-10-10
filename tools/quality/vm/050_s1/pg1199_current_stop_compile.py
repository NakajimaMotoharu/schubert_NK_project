"""New-only current D5 owned-stop compile against qualified current helper ABI."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1198_current_stop_binding import generate, SOURCE, BEFORE, OWNED

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def proof():
    d=json.loads((W/'pg1197-completed-current-before-v1.safe.json').read_bytes())
    if d['actualExit']!=0 or d['privateBeforeSha256']!=BEFORE or not d['currentFourOwnedLive'] or not d['newMetadataReferencesNormalClose']:
        raise ValueError('actual full same current seal required')
    if (W/'pg1195-chr-a01-native-v1.exit').read_bytes()!=b'0\n':
        raise ValueError('actual sameSource A01 required')
    return dict(d,productionSource=SOURCE,batchRun='343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
                cutoff='2026-10-10T12:40:27.396847Z',activation='ada3f7ff-8287-48d7-9ba9-5cce71f61bd3',
                beforeSha256=BEFORE,parentEndedUTC='2026-10-10T17:37:58.505406Z',
                ownedUnits={u:dict(MainPID=p,InvocationID=i,ActiveState='active',SubState='running')for u,(p,i)in OWNED.items()})


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean frozen source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    generated=generate(proof())
    subprocess.run(['python3','-B',str(R/'pg1198_current_stop_binding_test.py')],check=True)
    frozen=json.loads((W/'pg1175-runtime-frozen-v2.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('qualified current helper ABI required')
    target=W/'pg1198-native-tools-v1';target.mkdir(mode=0o700)
    for name,digest in frozen['fileHashes'].items():
        original=W/'pg1172-runtime-tools-v2'/name
        if hashlib.sha256(original.read_bytes()).hexdigest()!=digest:raise ValueError('immutable helper SHA refused')
        if name.endswith('.class'):
            dst=target/name;dst.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            with dst.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(original.read_bytes())
    for name,raw in generated.items():
        if name.endswith('.py'):ast.parse(raw)
        with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
    release=W/'pg1068-release-v1'
    cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(m2/x)for x in('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();phases={}
    for phase,args in [('compile',[str(J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(target),str(target/'Pg1198NativeStop.java'),str(target/'Pg1198NativeArgumentTest.java')]),('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1198NativeArgumentTest'])]:
        log=W/('pg1199-'+phase+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        with(W/('pg1199-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
        phases[phase]={'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        if r.returncode:print(json.dumps({'phase':phase,**phases[phase]}));return r.returncode
    files={str(f.relative_to(target)):hashlib.sha256(f.read_bytes()).hexdigest()for f in target.rglob('*')if f.is_file()}
    for f in target.rglob('*'):
        if f.is_file():f.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True)
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=head:raise ValueError('source changed during compile')
    safe={'actualExit':0,'operatorSource':head,'productionSource':SOURCE,'genuineParentBeforeSha256':BEFORE,'fileHashes':files,'phases':phases,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg1199-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}));return 0


if __name__=='__main__':raise SystemExit(main())
