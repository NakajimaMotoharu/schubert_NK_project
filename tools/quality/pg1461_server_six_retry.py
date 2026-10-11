"""New-only whole six after fixed Postgres fixture root qualification; old1460 retained."""
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
PGROOT=Path('/home/mini/codex/project1/work/characterization-tools/root/usr')


def runtime_hashes():
    paths=[PGROOT/'lib/postgresql',PGROOT/'share/postgresql',PGROOT/'lib/x86_64-linux-gnu']
    result={}
    for root in paths:
        for p in root.rglob('*'):
            if p.is_file():result[str(p.relative_to(PGROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    if not result:raise ValueError('fixed Postgres runtime required')
    return result


def source():return Path(full.__file__).read_text().replace('PG1459','PG1461')


def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    os.umask(0o077);out=W/'pg1461-server-six-v1';out.mkdir(mode=0o700)
    hashes=runtime_hashes()
    check=r'''import pathlib,hashlib,json,os,subprocess
root=pathlib.Path('/home/mini/schubert-nk-pgpt/tools/postgresql18/usr')
for name,digest in HASHES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
env={**os.environ,'LD_LIBRARY_PATH':str(root/'lib/x86_64-linux-gnu')+':'+str(root/'lib/postgresql/18/lib')}
versions={}
for name in ['postgres','initdb','pg_ctl','psql','pg_dump','pg_restore']:
 r=subprocess.run([str(root/'lib/postgresql/18/bin'/name),'--version'],capture_output=True,env=env,timeout=15);assert r.returncode==0;versions[name]=r.stdout.decode().strip()
for binary in ['bin/postgres','bin/initdb','lib/pgcrypto.so']:
 r=subprocess.run(['ldd',str(root/'lib/postgresql/18'/binary)],capture_output=True,env=env,timeout=15);assert r.returncode==0 and b'not found'not in r.stdout+r.stderr
print(json.dumps({'files':len(HASHES),'versions':versions,'missingLibraries':0,'sameHostToolHashes':True,'serviceStarted':False},sort_keys=True))
'''
    code,status=run('python3 -c '+__import__('shlex').quote('HASHES='+repr(hashes)+'\n'+check),timeout=120);assert code==0
    qualification=json.loads(status.strip())
    with(out/'postgres-runtime.safe.json').open('x')as f:json.dump({'qualification':qualification,'hashes':hashes,'source':'existing qualified host extracted Ubuntu packages, no DB/credential copied'},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    code,status=run('test -x /usr/bin/setfacl && test ! -e '+REMOTE+'/source-full-PG1461 && test ! -e '+REMOTE+'/tools/pg1461_server_six.py && mkdir -m700 '+REMOTE+'/source-full-PG1461 && tar -xf '+REMOTE+'/transfer/source.tar -C '+REMOTE+'/source-full-PG1461',timeout=120);assert code==0
    raw=source().encode();file=out/'pg1461_server_six.py'
    with file.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    code,status=copy(str(file),REMOTE+'/tools/pg1461_server_six.py',timeout=120);assert code==0
    code,status=run('sha256sum '+REMOTE+'/tools/pg1461_server_six.py',timeout=60);assert code==0 and hashlib.sha256(raw).hexdigest()in status
    with(out/'begin.safe.json').open('x')as f:json.dump({'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'helperSha256':hashlib.sha256(raw).hexdigest(),'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','sourceSnapshot':'2c29d7a17a5eca2f61b24e99af13260a3c286a09','old1459_1460Preserved':True,'formalAccepted':False},f);f.flush();os.fsync(f.fileno())
    code,status=run('python3 -B '+REMOTE+'/tools/pg1461_server_six.py',timeout=2400)
    with(out/'observer.private.log').open('x')as f:f.write(status);f.flush();os.fsync(f.fileno())
    with(out/'manifest.safe.json').open('x')as f:json.dump({'run':'PG1461-server-six','actualExit':code,'helperSha256':hashlib.sha256(raw).hexdigest(),'xmlSourceQualificationPending':True,'formalAccepted':False},f);f.flush();os.fsync(f.fileno())
    print(json.dumps({'run':'PG1461-server-six','actualExit':code,'xmlSourceQualificationPending':True,'formalAccepted':False}));return code


if __name__=='__main__':raise SystemExit(main())
