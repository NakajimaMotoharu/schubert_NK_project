"""New-only twenty-source current ABI compile; no guest mutations or old tools patch."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg1868_warning_candidate_ro_compile import J
from pg1645_completed_candidate_compile_v2 import canonical_relative,inventory
from pg2304_current_completed_resume_sources import sources,TOOLS,CLASS,SOURCE,BOM,BEFORE

TARGET=W/TOOLS


def write(path,data):
    canonical_relative(str(path.relative_to(TARGET)))
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with path.open('xb')as stream:
        os.fchmod(stream.fileno(),0o400)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    generated=sources()
    prior=json.loads((W/'pg2275-frozen-v1.safe.json').read_bytes())
    post=json.loads((W/'pg2281-current-signed-owned-post-v2/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!=SOURCE or post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0'] or post['proofHashes']['after.private.json']['sha256']!=BEFORE:
        raise ValueError('qualified current completed stop/post required')
    os.umask(0o077)
    TARGET.mkdir(mode=0o700)
    old=W/'pg2274-current-signed-owned-stop-tools-v1'
    for name,digest in prior['fileHashes'].items():
        canonical_relative(name)
        if not name.endswith('.class')or name.startswith('Pg2274'):continue
        data=(old/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('qualified current shared ABI byte required')
        write(TARGET/name,data)
    for name,raw in generated.items():write(TARGET/name,raw.encode())
    release=W/'pg2126-release-v1'
    cp=':'.join(str(p)for p in [TARGET,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*'])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/p)for p in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),*[str(TARGET/n)for n in sorted(generated)if n.endswith('.java')]])]
    commands.extend((name,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,clazz])for name,clazz in [('argument','Pg2304NativeArgumentTest'),('labelmount','Pg2304StopLabelTest'),('original','Pg2304OriginalTupleTest'),('identity','Pg2304CurrentIdentityTest'),('input','Pg2304InputBoundaryTest')])
    phases={};started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for label,args in commands:
        log=W/('pg2305-'+label+'-v1.private.log')
        with log.open('xb')as stream:
            result=subprocess.run(args,stdout=stream,stderr=stream)
            stream.flush();os.fsync(stream.fileno())
        phases[label]={'actualExit':result.returncode,'logSha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        if result.returncode:break
    hashes=inventory(TARGET)
    for path in TARGET.rglob('*'):
        if path.is_file():path.chmod(0o400)
    write(TARGET/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    fixed=head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain'])
    value={'actualExit':result.returncode,'operatorSource':head,'sourceQualified':fixed and result.returncode==0,'productionSource':SOURCE,'candidateManifestSha256':BOM,'genuineParentBeforeSha256':BEFORE,'fileHashes':hashes,'phases':phases,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    with(W/'pg2305-frozen-v1.safe.json').open('x')as stream:json.dump(value,stream,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k!='fileHashes'}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
