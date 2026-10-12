"""Direct whole RO compiler: immutable shared bytes, all generated source globals/ABI."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg1645_completed_candidate_compile_v2 import canonical_relative,inventory
from pg1867_warning_candidate_ro_sources import sources,TOOLS
from pg1844_warning_unit_full_six import CANDIDATE,OLD

TARGET=W/TOOLS
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(path,raw):
    canonical_relative(str(path.relative_to(TARGET)));path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with path.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    candidate=json.loads((W/'pg1846-candidate-build-v1.safe.json').read_bytes());post=json.loads((W/'pg1866-warning-unused-independent-post-v1/manifest.safe.json').read_bytes());prior=json.loads((W/'pg1861-frozen-v1.safe.json').read_bytes())
    if candidate['actualExit']!=post['actualExit']or candidate['actualExit']!=0 or candidate['candidateSource']!=CANDIDATE or post['candidateSource']!=CANDIDATE or post['productionSource']!=OLD or post['allClientAdvisoryFlock0']is not True or prior['actualExit']!=0:raise ValueError('actual full current/candidate and shared frozen ABI required')
    if post['candidateManifestSha256']!=candidate['manifestSha256']:raise ValueError('same actual candidate BOM required')
    os.umask(0o077);TARGET.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        canonical_relative(name)
        if not name.endswith('.class')or name.startswith('Pg1860'):continue
        p=W/'pg1860-warning-unused-tools-v1'/name
        if sha(p)!=digest:raise ValueError('actual qualified shared byte changed')
        write(TARGET/name,p.read_bytes())
    generated=sources(candidate['manifestSha256'],post['privateBeforeSha256'])
    bundle=(W/'pg1860-warning-unused-tools-v1/bundle.safe.json').read_bytes()
    generated['pg1867_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle).hexdigest())+'\n'+generated['pg1867_native_refs.py']
    from pyflakes.api import check
    for name,raw in generated.items():
        if name.endswith('.py')and check(raw,'<actual candidate RO '+name+'>'):raise ValueError('all actual emitted Python static gate required')
        write(TARGET/name,raw.encode())
    release=W/'pg1638-release-v1';cp=':'.join(str(p)for p in [TARGET,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*'])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/p)for p in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),*[str(TARGET/n)for n in sorted(generated)if n.endswith('.java')]])]
    commands.extend((name,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,clazz])for name,clazz in [('argument','Pg1867NativeArgumentTest'),('labelmount','Pg1867StopLabelTest'),('original','Pg1867OriginalTupleTest'),('identity','Pg1867CurrentIdentityTest'),('input','Pg1867InputBoundaryTest')])
    phases={};started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name,args in commands:
        log=W/('pg1868-'+name+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases[name]={'actualExit':r.returncode,'logSha256':sha(log)}
        if r.returncode:break
    hashes=inventory(TARGET)
    for p in TARGET.rglob('*'):
        if p.is_file():p.chmod(0o400)
    write(TARGET/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    value={'actualExit':r.returncode,'operatorSource':operator,'productionSource':OLD,'candidateSource':CANDIDATE,'candidateManifestSha256':candidate['manifestSha256'],'genuineParentBeforeSha256':post['privateBeforeSha256'],'fileHashes':hashes,'phases':phases,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg1868-frozen-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k not in ['fileHashes','phases']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
