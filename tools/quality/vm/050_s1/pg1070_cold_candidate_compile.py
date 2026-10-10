"""Freeze unused candidate bundle and completed-cold owned operator, host only."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg1069_cold_candidate_sources import files,DIGEST,SOURCE
from pg601_stage_contract import check_members
from pg1038_cold_preparation_compile import ROOT,HERE,W,J,sha,write


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean source required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    out=W/'pg1069-cold-tools-v1';out.mkdir(mode=0o700)
    private=Path('/home/mini/codex/project1/work/pgpt-vm/private')
    bundle=private/'pg1071-release-v1.tar';release=W/'pg1068-release-v1'
    manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest).hexdigest()!=DIGEST:raise ValueError('candidate manifest changed')
    data=json.loads(manifest)
    if data['source']['commit']!=SOURCE or len(data['artifacts'])!=187:raise ValueError('candidate identity refused')
    for row in data['artifacts']:
        p=release/row['path']
        if p.is_symlink()or p.stat().st_size!=row['size']or sha(p)!=row['sha256']:raise ValueError('candidate artifact changed')
    with tarfile.open(bundle,'x:')as tar:
        for p in sorted(release.rglob('*')):
            if p.is_symlink():raise ValueError('candidate symlink refused')
            tar.add(p,arcname=p.relative_to(release).as_posix(),recursive=False)
    with tarfile.open(bundle,'r:')as tar:
        check_members(tar.getmembers(),{r['path']for r in data['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'})
    signature=private/'pg1068-manifest-v1.sig'
    if signature.stat().st_size!=64 or sha(signature)!='5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b':raise ValueError('candidate signature changed')
    bundle_record={'archiveSha256':sha(bundle),'signatureSha256':sha(signature)}
    write(out/'bundle.safe.json',json.dumps(bundle_record,sort_keys=True).encode())
    previous=json.loads((W/'pg983-frozen-v3.safe.json').read_bytes())
    if previous['actualExit']!=0 or previous['productionSource']!='40ef6e894573d2ffab1d1732124960f9c98d5f97':raise ValueError('qualified helpers required')
    for name,digest in previous['fileHashes'].items():
        p=W/'pg983-bootstrap-tools-v3'/name
        if sha(p)!=digest:raise ValueError('qualified helper changed')
        if name.endswith('.class'):write(out/name,p.read_bytes())
    for name,text in files().items():
        if name.endswith('.py'):
            text='BUNDLE_HASH='+repr(sha(out/'bundle.safe.json'))+'\n'+text
            ast.parse(text)
        write(out/name,text.encode())
    current=W/'pg932-release-v1'
    cp=':'.join(map(str,[out,current/'api/api.jar',current/'operations/batch.jar',current/'api/lib/*',current/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('python-oracle',['python3','-B',str(HERE/'pg1069_cold_candidate_sources_test.py'),'-v']),
              ('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/'Pg1069ColdCandidateStage.java'),str(out/'Pg1069ColdCandidateStageTest.java')]),
              ('java-oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1069ColdCandidateStageTest'])]
    phases=[]
    for phase,command in commands:
        log=out/(phase+'.private.log')
        with log.open('xb')as f:
            r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'phase':phase,'actualExit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=operator:raise ValueError('source moved during compile')
    hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()}
    for p in out.iterdir():p.chmod(0o400)
    write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    value={'run':'PG1070-cold-candidate-compile-v1','actualExit':phases[-1]['actualExit'],'operatorSource':operator,'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','candidateSource':SOURCE,'candidateManifestSha256':DIGEST,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':phases,'fileHashes':hashes,'bundle':bundle_record,'guestActions':0,'formalAccepted':False,'fullColdPreparationAccepted':False}
    write(W/'pg1070-cold-candidate-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in value.items()if k not in ('phases','fileHashes','bundle')}));raise SystemExit(value['actualExit'])


if __name__=='__main__':main()
