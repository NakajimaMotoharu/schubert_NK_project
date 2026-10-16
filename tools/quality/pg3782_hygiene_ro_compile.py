"""Host-only immutable full RO ABI; reuses qualified shared classes, not old authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
from bundle_hash_contract import require_bound
from pg1645_completed_candidate_compile_v2 import canonical_relative
import pg3780_hygiene_ro_sources as role
from pg1446_current_cold_stage import W

TARGET=W/role.TOOLS
PRIOR=W/'pg3766-hygiene-unused-tools-v2'
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,raw):
    canonical_relative(path.relative_to(TARGET).as_posix())
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with path.open('xb')as f:
        os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())


def generated():
    values=role.sources()
    digest=sha(PRIOR/'bundle.safe.json')
    values['pg3780_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg3780_native_refs.py']
    require_bound(values['pg3780_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<all actual RO emitted Python>'):raise ValueError('actual namespace invalid')
    return values


def main():
    role.qualify()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    prior=json.loads((W/'pg3768-frozen-v1.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['candidateSource']!=role.SOURCE or prior['productionSource']!=role.CURRENT or prior['candidateManifestSha256']!=role.BOM:raise ValueError('actual fixed shared ABI required')
    for name,digest in prior['fileHashes'].items():
        canonical_relative(name)
        if sha(PRIOR/name)!=digest:raise ValueError('qualified shared input changed')
    values=generated();os.umask(0o077);TARGET.mkdir(mode=0o700)
    for name in prior['fileHashes']:
        if name.endswith('.class')and not name.startswith('Pg3766'):write(TARGET/name,(PRIOR/name).read_bytes())
    for name,raw in values.items():write(TARGET/name,raw.encode())
    cp=':'.join(str(p)for p in [TARGET,W/'pg3420-release-v1/api/api.jar',W/'pg3420-release-v1/operations/batch.jar',W/'pg3420-release-v1/api/lib/*',W/'pg3420-release-v1/operations/lib/*'])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/p)for p in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),*[str(TARGET/n)for n in sorted(values)if n.endswith('.java')]])]
    commands.extend((name,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,role.CLASS.replace('CandidateRo',suffix)])for name,suffix in [('argument','NativeArgumentTest'),('labelmount','StopLabelTest'),('original','OriginalTupleTest'),('identity','CurrentIdentityTest'),('input','InputBoundaryTest')])
    phases={};started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=None
    for name,args in commands:
        log=W/('pg3782-'+name+'-v1.private.log')
        with log.open('xb')as f:
            result=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        code=result.returncode;phases[name]={'actualExit':code,'logSha256':sha(log)}
        if code:break
    hashes={p.relative_to(TARGET).as_posix():sha(p)for p in TARGET.rglob('*')if p.is_file()}
    for p in TARGET.rglob('*'):
        if p.is_file():p.chmod(0o400)
    write(TARGET/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    value={'actualExit':code,'operatorSource':operator,'productionSource':role.CURRENT,'candidateSource':role.SOURCE,'candidateManifestSha256':role.BOM,'genuineParentBeforeSha256':role.BEFORE,'fileHashes':hashes,'phases':phases,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg3782-frozen-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k not in ['fileHashes','phases']}));return code


if __name__=='__main__':raise SystemExit(main())
