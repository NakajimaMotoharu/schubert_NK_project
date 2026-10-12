"""Fresh immutable current partial hostRO operator, old/current byte preserved."""
import json
import os
import subprocess
from pathlib import Path
from pg1442_current_cold_compile import ROOT,W,J,write,sha
from pg1546_pending_candidate_ro_sources import CLASS,TOOLS,java,refs,argument_test,BOM

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    closing=json.loads((W/'pg1545-pending-unused-independent-closing-v1/manifest.safe.json').read_bytes())
    if closing['actualExit']!=0 or not closing['guest']['unusedCandidateSigned187Qualified'] or not closing['guest']['candidateNotActivated']:
        raise ValueError('actual unused candidate independent closing required')
    prior=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!='769ddb15cd735c25fef581b5f9850ef9d0053c0f':raise ValueError('current helper provenance required')
    out=W/TOOLS;out.mkdir(mode=0o700);build=W/'pg1547-pending-ro-build-v1';build.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        p=W/'pg1396-bootstrap-tools-v3'/name
        if sha(p)!=digest:raise ValueError('immutable helper hash changed')
        if name.endswith('.class'):write(out/name,p.read_bytes())
    write(out/(CLASS+'.java'),java().encode());write(out/'pg1546_pending_candidate_ro_refs.py',refs().encode());write(out/'Pg1546ReadonlyArgumentTest.java',argument_test().encode())
    release=W/'pg1292-release-v1';cp=':'.join(map(str,[out,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[['python3','-B',str(ROOT/'tools/quality/pg1546_pending_candidate_ro_sources_test.py')],[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/(CLASS+'.java')),str(out/'Pg1546ReadonlyArgumentTest.java')],[str(J/'java'),'-cp',cp,'Pg1546ReadonlyArgumentTest']]
    phases=[]
    for i,cmd in enumerate(commands):
        log=build/f'phase-{i}.private.log'
        with log.open('xb')as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'command':cmd,'exit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()};write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    for p in out.iterdir():p.chmod(0o400)
    value={'run':'PG1547-pending-candidate-ro-frozen-v1','actualExit':phases[-1]['exit'],'operatorSource':head,'productionSource':prior['productionSource'],'candidateSource':'4d6bcbddb417b76d27e52d5d9640752c300edccf','candidateManifestSha256':BOM,'phases':phases,'fileHashes':hashes,'vmActions':0,'formalAccepted':False}
    write(W/'pg1547-pending-candidate-ro-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode());print(json.dumps({k:v for k,v in value.items()if k not in ['phases','fileHashes']}));return value['actualExit']

if __name__=='__main__':raise SystemExit(main())
