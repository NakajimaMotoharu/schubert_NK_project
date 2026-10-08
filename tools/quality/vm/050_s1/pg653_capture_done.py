"""Fresh normal cohort PID1/DONE readonly receipt, never old success reuse."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
from pg609_capture_done import PAYLOAD as TEMPLATE

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload(run):
    identifier=uuid.UUID(run);assert str(identifier)==run and identifier.version==4
    assert run not in ('e49243d5-de84-4714-8612-6912ddc17e9e','3a53b979-fa01-47dd-92a6-7b26affcfb5c')
    raw=TEMPLATE
    for old,new in (
        ('23b14a44b10504172e030bbd6625926bf049fb5c','36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('3a53b979-fa01-47dd-92a6-7b26affcfb5c',run),('pg605-fresh-parent-v2','pg650-fresh-parent-v2'),
        ('f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be','ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22'),
        ('1207482','1826480'),('5a1acaa0c35e484c979401e3b6dfb36a','095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('87863','111752'),('86264628081','107901545407'),('0.1.0-PG600','0.1.0-PG631'),
        ('a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f','57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
        ('pg609-completed-readonly-v1','pg653-completed-readonly-v1'),('PG609-completed-readonly-v1','PG653-completed-readonly-v1'),
        ('require(0<len(raw)<=limit and p.lstat()==s)','require(0<len(raw)<=limit and metadata9(p.lstat())==metadata9(s) and not os.listxattr(p))'),
        ('def strict(p,limit):','def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)\ndef strict(p,limit):'),
        ("'wholeFormalAccepted':False}))", "'wholeFormalAccepted':False,'ownedUnits':{u:{k:v[k]for k in ('MainPID','InvocationID','ExecMainStartTimestampMonotonic','ActiveState','SubState')}for u,v in after['units'].items()},'parentEndedUTC':done.decode('ascii').splitlines()[4]}))"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    assert(W/'pg651-observer-v1.exit').read_bytes()==b'0\n'and(W/'pg652-retention-post-v2.exit').read_bytes()==b'0\n'
    observed=json.loads((W/'pg651-watch-private-v1.jsonl').read_text().splitlines()[-1])
    assert observed['terminalObserved']and observed['parentExit']=='0'and observed['parentResult']=='success'
    assert set(observed['readyObserved'])==set(observed['rootsCaptured'])=={'api','web'}and observed['caddyTlsLogin200']
    post=json.loads((W/'pg652-retention-post-v2.safe.json').read_bytes());assert post['actualExit']==0 and post['retentionDeleted']==2 and post['eligibleAfter']==7
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('RECEIPT='+repr((R/'pg609_parent_receipt.py').read_text())+'\n'+payload(post['runId'])).encode(),capture_output=True,timeout=90)
    with(W/'pg653-completed-readonly-v1.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with(W/'pg653-completed-readonly-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout);assert safe['cutoff']==post['cutoff']
        safe.update(startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with(W/'pg653-completed-readonly-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
