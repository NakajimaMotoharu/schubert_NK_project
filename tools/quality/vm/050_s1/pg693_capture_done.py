"""New current-source genuine PID1/DONE receipt, readonly only."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg653_capture_done import payload as previous_payload
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload(run):
    assert run!='601297d0-a8ba-47da-852b-0ffeae409965'
    return replace(previous_payload(run),(
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('pg650-fresh-parent-v2','pg690-fresh-parent-v1'),
        ('ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22','c2a125086080538d44a434dd3313999d45d075a7debab2f103e984908707d982'),
        ('1826480','2146618'),('095f6d1d7f8442b7b2b44ae59a4314f5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('111752','122726'),('107901545407','119288459330'),('0.1.0-PG631','0.1.0-PG682'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('pg653-completed-readonly-v1','pg693-completed-readonly-v1'),('PG653-completed-readonly-v1','PG693-completed-readonly-v1'),
    ))


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])
    assert(W/'pg691-observer-v1.exit').read_bytes()==b'0\n'and(W/'pg692-retention-post-v1.exit').read_bytes()==b'0\n'
    observed=json.loads((W/'pg691-watch-private-v1.jsonl').read_text().splitlines()[-1])
    assert observed['terminalObserved']and observed['parentExit']=='0'and observed['parentResult']=='success'
    assert set(observed['readyObserved'])==set(observed['rootsCaptured'])=={'api','web'}and observed['caddyTlsLogin200']
    post=json.loads((W/'pg692-retention-post-v1.safe.json').read_text())
    assert post['actualExit']==0 and post['retentionDeleted']==1 and post['eligibleAfter']==7
    log=W/'pg693-completed-readonly-v1.private.log';assert not log.exists()
    assert not(W/'pg693-completed-readonly-v1.safe.json').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('RECEIPT='+repr((R/'pg685_parent_receipt.py').read_text())+'\n'+payload(post['runId'])).encode(),capture_output=True,timeout=90)
    with log.open('xb')as stream:stream.write(result.stderr);stream.flush();os.fsync(stream.fileno())
    with(W/'pg693-completed-readonly-v1.exit').open('x')as stream:stream.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout);assert safe['cutoff']==post['cutoff']
        safe.update(startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip())
        with(W/'pg693-completed-readonly-v1.safe.json').open('x')as stream:json.dump(safe,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
