"""Freeze fresh owned-stop sources, same D5 ABI, actual constructor/CLI tests."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1247_fresh_owned_stop_sources import sources,SOURCE,BEFORE,W

J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
TARGET=W/'pg1247-native-tools-v1'

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    generated=sources();compile_started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if os.path.lexists(TARGET):raise ValueError('new-only immutable tools required')
    prior=json.loads((W/'pg1217-frozen-v1.safe.json').read_bytes())
    TARGET.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        if not name.endswith('.class')or name.startswith('Pg1216'):continue
        raw=(W/'pg1216-native-tools-v1'/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('qualified immutable ABI hash refused')
        path=TARGET/name;path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        with path.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
    for name,raw in generated.items():
        with(TARGET/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
    release=W/'pg1068-release-v1'
    cp=':'.join(map(str,(TARGET,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(m2/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    phases={}
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),*[str(TARGET/n)for n in ['Pg1247NativeStop.java','Pg1247NativeArgumentTest.java','Pg1247StopLabelTest.java']]])]+[(label,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,clazz])for label,clazz in [('oracle','Pg1247NativeArgumentTest'),('label','Pg1247StopLabelTest')]]
    for label,args in commands:
        log=W/('pg1248-'+label+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases[label]={'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        if r.returncode:print(json.dumps({'phase':label,**phases[label]}));return r.returncode
    hashes={str(p.relative_to(TARGET)):hashlib.sha256(p.read_bytes()).hexdigest()for p in TARGET.rglob('*')if p.is_file()}
    for p in TARGET.rglob('*'):
        if p.is_file():p.chmod(0o400)
    with(TARGET/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(hashes,f,sort_keys=True)
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=head:raise ValueError('operator source changed during qualification')
    value={'actualExit':0,'operatorSource':head,'productionSource':SOURCE,'genuineParentBeforeSha256':BEFORE,'fileHashes':hashes,'phases':phases,'startedUTC':compile_started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg1248-frozen-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k!='fileHashes'}));return 0

if __name__=='__main__':raise SystemExit(main())
