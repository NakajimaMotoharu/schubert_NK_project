"""Source-fixed new-only SSC264 compiler using the qualified current769 ABI."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1441_current_cold_sources import java
from pg1441_current_cold_refs import source as observer

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=W/'pg1441-current-cold-tools-v1'
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):
    with path.open('xb') as f:os.fchmod(f.fileno(),0o400);f.write(data);f.flush();os.fsync(f.fileno())


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    prior=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())
    assert prior['actualExit']==0 and prior['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    OUT.mkdir(mode=0o700)
    for name,digest in prior['fileHashes'].items():
        p=W/'pg1396-bootstrap-tools-v3'/name
        assert sha(p)==digest
        if name.endswith('.class'):write(OUT/name,p.read_bytes())
    write(OUT/'Pg1441CurrentColdPreparation.java',java().encode())
    write(OUT/'pg1441_current_cold_refs.py',observer().encode())
    release=W/'pg1292-release-v1'
    cp=':'.join(map(str,[OUT,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in [
        'com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
        'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
        'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[['python3','-B',str(ROOT/'tools/quality/pg1441_current_cold_sources_test.py')],
        [str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(OUT),str(OUT/'Pg1441CurrentColdPreparation.java')]]
    phases=[]
    for index,command in enumerate(commands):
        log=OUT/('phase-'+str(index)+'.private.log')
        with log.open('xb')as f:
            r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'command':command,'exit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    hashes={p.name:sha(p)for p in OUT.iterdir() if p.is_file()}
    for p in OUT.iterdir():p.chmod(0o400)
    write(OUT/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    result={'run':'PG1442-current-cold-compile-v1','actualExit':phases[-1]['exit'],
            'operatorSource':head,'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f',
            'phases':phases,'fileHashes':hashes,'vmActions':0,'formalAccepted':False,
            'fullColdPreparationAccepted':False}
    write(W/'pg1442-current-cold-frozen-v1.safe.json',json.dumps(result,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in result.items() if k not in ['phases','fileHashes']}))
    return result['actualExit']


if __name__=='__main__':raise SystemExit(main())
