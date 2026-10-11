"""New-only selected source/tools; no credential, VM or deployed DB copy."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
REMOTE='/home/mini/schubert-nk-pgpt'


def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    os.umask(0o077);out=W/'pg1466-server-selected-v1';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=out/'source.tar'
    with archive.open('xb')as f:
        subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True)
        f.flush();os.fsync(f.fileno())
    helper=ROOT/'tools/quality/pg1466_server_selected.py'
    shell=Path('/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck')
    files=[(archive,REMOTE+'/transfer/PG1466-source.tar'),
           (helper,REMOTE+'/tools/pg1466_server_selected.py'),
           (shell,REMOTE+'/tools/shellcheck-0.11.0')]
    hashes={dest:hashlib.sha256(p.read_bytes()).hexdigest() for p,dest in files}
    code,status=run('test ! -e '+REMOTE+'/source-selected-PG1466 && test ! -e '+REMOTE+'/runs/PG1466-selected-v1 && '+' && '.join('test ! -e '+dest for _,dest in files))
    assert code==0
    for p,dest in files:
        code,status=copy(str(p),dest,timeout=300);assert code==0
    code,status=run('sha256sum '+' '.join(hashes)+'; '+REMOTE+'/tools/shellcheck-0.11.0 --version')
    assert code==0 and all(h in status for h in hashes.values()) and 'version: 0.11.0' in status
    with(out/'begin.safe.json').open('x')as f:
        json.dump({'sourceSnapshot':head,'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f',
                   'transferHashes':hashes,'formalAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    code,status=run('mkdir -m700 '+REMOTE+'/source-selected-PG1466 && tar -xf '+REMOTE+'/transfer/PG1466-source.tar -C '+REMOTE+'/source-selected-PG1466',timeout=120)
    assert code==0
    code,status=run('python3 -B '+REMOTE+'/tools/pg1466_server_selected.py',timeout=1200)
    with(out/'observer.private.log').open('x')as f:f.write(status);f.flush();os.fsync(f.fileno())
    manifest={'run':'PG1466-server-selected','actualExit':code,'sourceSnapshot':head,
              'sourceQualificationPending':True,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest,sort_keys=True));return code


if __name__=='__main__':raise SystemExit(main())
