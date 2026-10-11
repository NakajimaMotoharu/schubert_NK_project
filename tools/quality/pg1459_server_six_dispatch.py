"""Copy only fixed Node + helper; reuse qualified source archive into new target."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
ROOT=Path(__file__).resolve().parents[2]
REMOTE='/home/mini/schubert-nk-pgpt'


def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    os.umask(0o077);out=W/'pg1459-server-six-v1';out.mkdir(mode=0o700)
    node=Path('/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node');node_sha=hashlib.sha256(node.read_bytes()).hexdigest()
    helper=ROOT/'tools/quality/pg1459_server_six.py';helper_sha=hashlib.sha256(helper.read_bytes()).hexdigest()
    with(out/'begin.safe.json').open('x')as f:json.dump({'sourceSnapshot':'2c29d7a17a5eca2f61b24e99af13260a3c286a09','productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'nodeSha256':node_sha,'helperSha256':helper_sha,'formalAccepted':False},f);f.flush();os.fsync(f.fileno())
    status,output=run('test ! -e '+REMOTE+'/tools/node-v24.19.0 && test ! -e '+REMOTE+'/tools/pg1459_server_six.py && test ! -e '+REMOTE+'/source-full-PG1459 && mkdir -m700 '+REMOTE+'/source-full-PG1459 && tar -xf '+REMOTE+'/transfer/source.tar -C '+REMOTE+'/source-full-PG1459',timeout=120)
    assert status==0
    for src,dest in[(str(node.parent.parent),REMOTE+'/tools/'),(str(helper),REMOTE+'/tools/pg1459_server_six.py')]:
        code,stats=copy(src,dest,timeout=300);assert code==0
    code,result=run('sha256sum '+REMOTE+'/tools/node-v24.19.0/bin/node '+REMOTE+'/tools/pg1459_server_six.py; '+REMOTE+'/tools/node-v24.19.0/bin/node --version',timeout=60)
    assert code==0 and node_sha in result and helper_sha in result and 'v24.19.0'in result
    code,result=run('python3 -B '+REMOTE+'/tools/pg1459_server_six.py',timeout=2400)
    with(out/'observer.private.log').open('x')as f:f.write(result);f.flush();os.fsync(f.fileno())
    with(out/'manifest.safe.json').open('x')as f:json.dump({'actualExit':code,'nodeSha256':node_sha,'helperSha256':helper_sha,'privateLogSha256':hashlib.sha256(result.encode()).hexdigest(),'serverResultManifest':REMOTE+'/runs/PG1459-six-v1/manifest.safe.json','formalAccepted':False,'xmlSourceQualificationPending':True},f);f.flush();os.fsync(f.fileno())
    print(json.dumps({'run':'PG1459-server-six','actualExit':code,'xmlSourceQualificationPending':True,'formalAccepted':False}));return code


if __name__=='__main__':raise SystemExit(main())
