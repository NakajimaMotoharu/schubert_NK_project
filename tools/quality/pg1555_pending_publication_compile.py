"""Freeze no-epoch partial publication operator; fixed old classpath for lifetime."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1442_current_cold_compile import ROOT,W,J,write,sha
from pg1546_pending_candidate_ro_sources import argument_test,BOM
from pg1553_pending_publication_java import CLASS,TOOLS,java
from pg1553_pending_publication_refs import source

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    closing=json.loads((W/'pg1550-pending-candidate-ro-independent-closing-v1/manifest.safe.json').read_bytes())
    if closing['actualExit']!=0:raise ValueError('actual independent hostRO closing required')
    prior=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!='769ddb15cd735c25fef581b5f9850ef9d0053c0f':raise ValueError('current helper provenance required')
    out=W/TOOLS;out.mkdir(mode=0o700);build=W/'pg1555-pending-publication-build-v1';build.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        p=W/'pg1396-bootstrap-tools-v3'/name
        if sha(p)!=digest:raise ValueError('immutable helper hash changed')
        if name.endswith('.class'):write(out/name,p.read_bytes())
    write(out/(CLASS+'.java'),java().encode());write(out/'pg1553_pending_publication_refs.py',source().encode())
    test=argument_test().replace('Pg1546ReadonlyArgumentTest','Pg1555PublicationArgumentTest').replace('Pg1546PendingCandidateHostRo',CLASS).replace('"prepare-ro"','"activate"')
    write(out/'Pg1555PublicationArgumentTest.java',test.encode())
    for name in ['pg1551_pending_publication_contract.py','pg1552_publication_inventory.py','pg1554_pending_exchange_io.py']:
        write(out/name,(ROOT/'tools/quality'/name).read_bytes())
    for name in ['pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py']:
        write(out/name,(ROOT/'tools/quality/vm/050_s1'/name).read_bytes())
    release=W/'pg1292-release-v1';cp=':'.join(map(str,[out,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[['python3','-B',str(ROOT/'tools/quality/pg1553_pending_publication_sources_test.py')],['python3','-B',str(ROOT/'tools/quality/pg1551_pending_publication_contract_test.py')],['python3','-B',str(ROOT/'tools/quality/pg1552_publication_inventory_test.py')],['python3','-B',str(ROOT/'tools/quality/pg1554_pending_exchange_io_test.py')],[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/(CLASS+'.java')),str(out/'Pg1555PublicationArgumentTest.java')],[str(J/'java'),'-cp',cp,'Pg1555PublicationArgumentTest'],['python3','-B','-m','pyflakes',str(out/'pg1553_pending_publication_refs.py')],['python3','-B','-c',"import pg1551_pending_publication_contract,pg1552_publication_inventory,pg1554_pending_exchange_io,pg1090_cold_finite_capture;assert pg1551_pending_publication_contract.PHASES[-1]=='release'"]]
    env=dict(os.environ);env['PYTHONPATH']=str(out)+':/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime'
    phases=[]
    for i,cmd in enumerate(commands):
        log=build/f'phase-{i}.private.log'
        with log.open('xb')as f:r=subprocess.run(cmd,cwd=out if i==7 else ROOT,env=env,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'command':cmd,'exit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()};write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    for p in out.iterdir():p.chmod(0o400)
    value={'run':'PG1555-pending-publication-frozen-v1','actualExit':phases[-1]['exit'],'operatorSource':head,'productionSource':prior['productionSource'],'candidateSource':'4d6bcbddb417b76d27e52d5d9640752c300edccf','candidateManifestSha256':BOM,'phases':phases,'fileHashes':hashes,'closingManifestSha256':hashlib.sha256((W/'pg1550-pending-candidate-ro-independent-closing-v1/manifest.safe.json').read_bytes()).hexdigest(),'vmActions':0,'formalAccepted':False}
    write(W/'pg1555-pending-publication-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode());print(json.dumps({k:v for k,v in value.items()if k not in ['phases','fileHashes']}));return value['actualExit']

if __name__=='__main__':raise SystemExit(main())
