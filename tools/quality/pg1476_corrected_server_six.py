"""Necessary fresh full six after qualified static/auth correction; no VM mutation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg1459_server_six as previous
from lan_server import copy,run

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
REMOTE='/home/mini/schubert-nk-pgpt'


def server_source(head,archive_sha):
    if not (type(head)is str and len(head)==40 and type(archive_sha)is str and len(archive_sha)==64
            and all(c in '0123456789abcdef'for c in head+archive_sha)):
        raise ValueError('fixed source/archive identity required')
    raw=Path(previous.__file__).read_text().replace('PG1459','PG1476')
    raw=raw.replace(previous.ARCHIVE_SHA,archive_sha).replace("BASE/'transfer/source.tar'","BASE/'transfer/PG1476-source.tar'")
    raw=raw.replace('2c29d7a17a5eca2f61b24e99af13260a3c286a09',head).replace('3576','3578')
    old="'SCHUBERT_PG_ROOT':str(BASE/'tools/postgresql18/usr')}"
    assert raw.count(old)==1
    raw=raw.replace(old,"'SCHUBERT_PG_ROOT':str(BASE/'tools/postgresql18/usr'),'SCHUBERT_SHELLCHECK':str(BASE/'tools/shellcheck-0.11.0')}")
    compile(raw,'<new corrected full six>','exec');return raw


def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    qualified=json.loads((W/'pg1474-selected-qualification-v1/manifest.safe.json').read_bytes())
    assert qualified['actualExit']==0 and qualified['freshTests']==21 and qualified['staticIssues']==0 and qualified['allApiMainClassBytesEqual1279'] is True
    os.umask(0o077);out=W/'pg1476-server-six-v1';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=out/'source.tar'
    with archive.open('xb')as f:
        subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
    raw=server_source(head,hashlib.sha256(archive.read_bytes()).hexdigest())
    helper=out/'pg1476_server_six.py';helper.write_text(raw)
    files=[(archive,REMOTE+'/transfer/PG1476-source.tar'),(helper,REMOTE+'/tools/pg1476_server_six.py')]
    hashes={dest:hashlib.sha256(p.read_bytes()).hexdigest()for p,dest in files}
    code,status=run('test ! -e '+REMOTE+'/source-full-PG1476 && test ! -e '+REMOTE+'/runs/PG1476-six-v1 && '+' && '.join('test ! -e '+dest for _,dest in files));assert code==0
    for p,dest in files:
        code,status=copy(str(p),dest,timeout=300);assert code==0
    code,status=run('sha256sum '+' '.join(hashes));assert code==0 and all(h in status for h in hashes.values())
    shell=Path('/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck')
    code,status=run('sha256sum '+REMOTE+'/tools/shellcheck-0.11.0; '+REMOTE+'/tools/shellcheck-0.11.0 --version');assert code==0 and hashlib.sha256(shell.read_bytes()).hexdigest()in status and 'version: 0.11.0'in status
    with(out/'begin.safe.json').open('x')as f:
        json.dump({'snapshot':head,'transferHashes':hashes,'expectedTests':3578,'expectedSuites':523,'expectedClasses':1635,'expectedCountBasis':'PG1279 3569 + seven pre-reset tests + Unit negative1 + DB timeout1, no new test suite','trigger':'SSC267/new two independent negative tests and fixed static fixture; prior whole campaigns failed, qualified selected21 only','oldFailuresRetained':True,'formalAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    code,status=run('mkdir -m700 '+REMOTE+'/source-full-PG1476 && tar -xf '+REMOTE+'/transfer/PG1476-source.tar -C '+REMOTE+'/source-full-PG1476',timeout=120);assert code==0
    code,status=run('python3 -B '+REMOTE+'/tools/pg1476_server_six.py',timeout=3600)
    with(out/'observer.private.log').open('x')as f:f.write(status);f.flush();os.fsync(f.fileno())
    value={'run':'PG1476-server-six-v1','actualExit':code,'snapshot':head,'formalAccepted':False,'xmlSourceQualificationPending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True));return code


if __name__=='__main__':raise SystemExit(main())
