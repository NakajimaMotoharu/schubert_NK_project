"""Separate full-six new source/target and corrected fixture environment; old1459 kept."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg1459_server_six as full
from lan_server import copy,run

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
ROOT=Path(__file__).resolve().parents[2]
REMOTE='/home/mini/schubert-nk-pgpt'


def source():
    raw=Path(full.__file__).read_text()
    if 'PG1459'not in raw:raise ValueError('fixed old full source required')
    return raw.replace('PG1459','PG1460')


def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    os.umask(0o077);out=W/'pg1460-server-six-v1';out.mkdir(mode=0o700)
    raw=source().encode();file=out/'pg1460_server_six.py'
    with file.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    code,status=run('test -x /usr/bin/setfacl && test -x /usr/bin/getfacl && test ! -e '+REMOTE+'/source-full-PG1460 && test ! -e '+REMOTE+'/tools/pg1460_server_six.py && mkdir -m700 '+REMOTE+'/source-full-PG1460 && tar -xf '+REMOTE+'/transfer/source.tar -C '+REMOTE+'/source-full-PG1460',timeout=120);assert code==0
    code,status=copy(str(file),REMOTE+'/tools/pg1460_server_six.py',timeout=120);assert code==0
    code,status=run('sha256sum '+REMOTE+'/tools/pg1460_server_six.py; /usr/bin/setfacl --version; /usr/bin/getfacl --version',timeout=60);assert code==0 and hashlib.sha256(raw).hexdigest()in status
    with(out/'begin.safe.json').open('x')as f:json.dump({'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'helperSha256':hashlib.sha256(raw).hexdigest(),'sourceSnapshot':'2c29d7a17a5eca2f61b24e99af13260a3c286a09','productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','old1459Exit':1,'oldTargetPreserved':True,'fixtureChildUmask':'0027','JAVA_TOOL_OPTIONS':'absent','formalAccepted':False},f);f.flush();os.fsync(f.fileno())
    code,status=run('python3 -B '+REMOTE+'/tools/pg1460_server_six.py',timeout=2400)
    with(out/'observer.private.log').open('x')as f:f.write(status);f.flush();os.fsync(f.fileno())
    with(out/'manifest.safe.json').open('x')as f:json.dump({'run':'PG1460-server-six','actualExit':code,'helperSha256':hashlib.sha256(raw).hexdigest(),'serverManifest':REMOTE+'/runs/PG1460-six-v1/manifest.safe.json','formalAccepted':False,'xmlSourceQualificationPending':True},f);f.flush();os.fsync(f.fileno())
    print(json.dumps({'run':'PG1460-server-six','actualExit':code,'xmlSourceQualificationPending':True,'formalAccepted':False}));return code


if __name__=='__main__':raise SystemExit(main())
