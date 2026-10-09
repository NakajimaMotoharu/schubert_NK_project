"""Actual current parent readonly Backup full-row post, original budget unchanged."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg692_retention_sources import capture,oracle

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])
    assert(W/'pg690-start-v1.exit').read_bytes()==b'0\n'
    log=W/'pg692-retention-post-v1.private.log';assert not log.exists()
    assert not(W/'pg692-retention-post-v1.safe.json').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    code='ORACLE='+repr(oracle())+'\n'+capture()
    with log.open('xb')as stream:
        result=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=stream);stream.flush();os.fsync(stream.fileno())
    with(W/'pg692-retention-post-v1.exit').open('x')as stream:stream.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout);safe['operatorSource']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip()
        with(W/'pg692-retention-post-v1.safe.json').open('x')as stream:json.dump(safe,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
