"""Current PID1 original-budget DONE, readonly; no old completed receipt reuse."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg693_capture_done import payload as previous
from pg724_retention_sources import bind
from pg662_sources import replace
from pg717_sources import receipt

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload(run):
    assert run!='8633b77f-77dc-4a78-88b4-41165f159b43'
    return replace(bind(previous(run)), (
        ('pg693-completed-readonly-v1','pg725-completed-readonly-v1'),
        ('PG693-completed-readonly-v1','PG725-completed-readonly-v1'),
    ))


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])
    assert (W/'pg723-observer-v1.exit').read_bytes()==b'0\n' and (W/'pg724-retention-post-v1.exit').read_bytes()==b'0\n'
    observed=json.loads((W/'pg723-watch-private-v1.jsonl').read_text().splitlines()[-1])
    assert observed['terminalObserved'] and observed['parentExit']=='0' and observed['parentResult']=='success'
    assert set(observed['readyObserved'])==set(observed['rootsCaptured'])=={'api','web'} and observed['caddyTlsLogin200']
    post=json.loads((W/'pg724-retention-post-v1.safe.json').read_bytes())
    assert post['actualExit']==0 and post['retentionDeleted']==1 and post['eligibleAfter']==7
    log=W/'pg725-completed-readonly-v1.private.log'; assert not log.exists()
    assert not (W/'pg725-completed-readonly-v1.safe.json').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('RECEIPT='+repr(receipt())+'\n'+payload(post['runId'])).encode(),capture_output=True,timeout=90)
    with log.open('xb') as f: f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with (W/'pg725-completed-readonly-v1.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout); assert safe['cutoff']==post['cutoff']
        safe.update(startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip())
        with (W/'pg725-completed-readonly-v1.safe.json').open('x') as f: json.dump(safe,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
        print(json.dumps(safe))
    else:
        print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__': main()
