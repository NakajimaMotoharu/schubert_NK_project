"""New-only current ABI hostRO compiler; reuse candidate, no new release archive."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg1642_completed_candidate_compile as engine
from pg1645_completed_candidate_compile_v2 import canonical_relative,inventory
from pg1686_completed_candidate_ro_sources import sources,TOOLS,BOM,SOURCE

TARGET=engine.W/TOOLS


def write(path,raw):
    canonical_relative(str(path.relative_to(TARGET)))
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    engine.write(path,raw)


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    post=json.loads((engine.W/'pg1685-unused-candidate-full-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['candidateSource']!=SOURCE or post['candidateManifestSha256']!=BOM or post['allClientAdvisoryFlock0']is not True:raise ValueError('actual signed unused full current post required')
    prior=json.loads((engine.W/'pg1682-frozen-v1.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!='4d6bcbddb417b76d27e52d5d9640752c300edccf':raise ValueError('qualified current ABI required')
    if os.path.lexists(TARGET):raise ValueError('new-only RO tools required')
    TARGET.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        canonical_relative(name)
        if not name.endswith('.class')or name.startswith(('Pg1640','Pg1660','Pg1681')):continue
        p=engine.W/'pg1681-completed-unused-tools-v4'/name
        if engine.sha(p)!=digest:raise ValueError('qualified shared class byte changed')
        write(TARGET/name,p.read_bytes())
    generated=sources()
    for name,raw in generated.items():write(TARGET/name,raw.encode())
    release=engine.W/'pg1544-release-v1'
    cp=':'.join(str(p)for p in [TARGET,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*'])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/p)for p in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    java=sorted(n for n in generated if n.endswith('.java'))
    commands=[('compile',[str(engine.J/'javac'),'-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),*[str(TARGET/n)for n in java]])]
    commands +=[(name,[str(engine.J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,clazz])for name,clazz in [('argument','Pg1686NativeArgumentTest'),('labelmount','Pg1686StopLabelTest'),('original','Pg1686OriginalTupleTest'),('identity','Pg1686CurrentIdentityTest'),('input','Pg1686InputBoundaryTest')]]
    phases={};started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name,command in commands:
        log=engine.W/('pg1687-'+name+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(command,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases[name]={'actualExit':r.returncode,'logSha256':engine.sha(log)}
        if r.returncode:break
    hashes=inventory(TARGET)
    for p in TARGET.rglob('*'):
        if p.is_file():p.chmod(0o400)
    engine.write(TARGET/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    value={'actualExit':r.returncode,'operatorSource':head,'productionSource':prior['productionSource'],'candidateSource':SOURCE,'candidateManifestSha256':BOM,'genuineParentBeforeSha256':post['privateBeforeSha256'],'fileHashes':hashes,'phases':phases,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutations0':True,'formalAccepted':False}
    engine.write(engine.W/'pg1687-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in value.items()if k not in ['fileHashes','phases']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
