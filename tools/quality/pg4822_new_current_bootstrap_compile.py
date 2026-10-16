"""SSC300 actual current JAR ABI, five phases, pinned current shared class graph; no VM."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
import pg4820_new_current_bootstrap_sources as role

W=role.W
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean operator first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    raw=role.files(role.BASELINE)
    for name,text in raw.items():
        if name.endswith('.py'):
            ast.parse(text)
            if check(text,name):raise ValueError('full emitted Python namespace must be static clean')
    old=W/'pg4772-new-current-owned-tools-v1'
    frozen=json.loads((W/'pg4774-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=role.SOURCE:raise ValueError('actual current shared ABI qualification required')
    target=W/role.TOOLS;target.mkdir(mode=0o700)
    shared={}
    for name,digest in frozen['fileHashes'].items():
        value=(old/name).read_bytes()
        if hashlib.sha256(value).hexdigest()!=digest:raise ValueError('shared current input bytes changed')
        if name.endswith('.class'):
            with(target/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(value)
            shared[name]=digest
    for name,value in raw.items():
        with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(value)
    release=W/'pg4702-release-v1'
    bom=(release/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(bom).hexdigest()!=role.BOM:raise ValueError('actual signed release BOM required')
    cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    phases=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),*[str(target/name)for name in raw if name.endswith('.java')]])]
    for phase,cls in [('oracle','BootstrapArgumentTest'),('input','BootstrapInputTest'),('expected','BootstrapExpectedTest'),('liveness','OwnedDatabaseTest')]:
        phases.append((phase,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg4820'+cls]))
    outcomes=[]
    for phase,args in phases:
        log=W/('pg4822-'+phase+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        with(W/('pg4822-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
        item={'phase':phase,'actualExit':r.returncode,'logSha256':hashlib.sha256(log.read_bytes()).hexdigest()};outcomes.append(item)
        if r.returncode:print(json.dumps(item));return r.returncode
    hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
    for p in target.iterdir():p.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(hashes,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=head:raise ValueError('source changed during qualification')
    value={'actualExit':0,'productionSource':role.SOURCE,'BOM':role.BOM,'operatorSource':head,'beforeSha256':role.BASELINE,'fileHashes':hashes,'sharedInputs':shared,'phases':outcomes,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg4822-frozen-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in ('fileHashes','sharedInputs')}));return 0


if __name__=='__main__':raise SystemExit(main())
