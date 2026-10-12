"""Freeze partial-original placement operator and closed signed input after full gate."""
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg1442_current_cold_compile import ROOT, W, J, write, sha
from pg1536_pending_candidate_sources import TOOLS, CLASS, java, refs

P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    candidate=json.loads((W/'pg1544-candidate-build-v1.safe.json').read_bytes())
    if candidate['actualExit']!=0 or not candidate['signatureVerified'] or candidate['candidateSource']!='4d6bcbddb417b76d27e52d5d9640752c300edccf' or not candidate['candidateNotDeployed']:
        raise ValueError('signed independently qualified candidate required')
    prior=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!='769ddb15cd735c25fef581b5f9850ef9d0053c0f':raise ValueError('current immutable helper qualification required')
    source=W/'pg1544-release-v1';signature=P/'pg1544-manifest-v1.sig'
    if sha(source/'RELEASE-MANIFEST.json')!=candidate['manifestSha256'] or sha(signature)!=candidate['signatureSha256']:raise ValueError('signed input changed')
    out=W/TOOLS;out.mkdir(mode=0o700);build=W/'pg1537-pending-unused-build-v1';build.mkdir(mode=0o700)
    archive=P/'pg1538-release-v1.tar'
    with tarfile.open(archive,'x:')as t:
        for path in sorted(source.rglob('*')):t.add(path,arcname=str(path.relative_to(source)),recursive=False)
    bundle=json.dumps({'archiveSha256':sha(archive),'signatureSha256':sha(signature)},sort_keys=True).encode()
    write(out/'bundle.safe.json',bundle)
    for name,digest in prior['fileHashes'].items():
        p=W/'pg1396-bootstrap-tools-v3'/name
        if sha(p)!=digest:raise ValueError('current frozen helper changed')
        if name.endswith('.class'):write(out/name,p.read_bytes())
    import hashlib
    bundle_hash=hashlib.sha256(bundle).hexdigest()
    write(out/(CLASS+'.java'),java().encode());write(out/'pg1536_pending_unused_refs.py',refs(candidate['manifestSha256'],bundle_hash).encode())
    release=W/'pg1292-release-v1';cp=':'.join(map(str,[out,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[['python3','-B',str(ROOT/'tools/quality/pg1536_pending_candidate_sources_test.py')],[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/(CLASS+'.java'))]]
    phases=[]
    for i,command in enumerate(commands):
        log=build/f'phase-{i}.private.log'
        with log.open('xb')as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'command':command,'exit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()};write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    for p in out.iterdir():p.chmod(0o400)
    value={'run':'PG1537-pending-unused-compile-v1','actualExit':phases[-1]['exit'],'operatorSource':head,'productionSource':prior['productionSource'],'candidateSource':candidate['candidateSource'],'candidateManifestSha256':candidate['manifestSha256'],'bundleSha256':bundle_hash,'archiveSha256':sha(archive),'fileHashes':hashes,'phases':phases,'vmActions':0,'formalAccepted':False}
    write(W/'pg1537-pending-unused-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in value.items()if k not in ['fileHashes','phases']}));return value['actualExit']

if __name__=='__main__':raise SystemExit(main())
