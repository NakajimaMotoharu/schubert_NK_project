"""New genuine resume DONE receipt: same strict PID1 oracle, explicit fixed cohort.

Read-only; no start/stop/repair. Reuses inspected capture structure, not old result.
"""
import hashlib
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg609_capture_done as previous

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
MANIFEST = '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'


def payload():
    value = previous.PAYLOAD
    bindings = [
        ('23b14a44b10504172e030bbd6625926bf049fb5c', SOURCE),
        ('3a53b979-fa01-47dd-92a6-7b26affcfb5c', 'e49243d5-de84-4714-8612-6912ddc17e9e'),
        ('pg605-fresh-parent-v2', 'pg637-fresh-resume-v2'),
        ('f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be',
         'c946eaae7147aff0fb328bfabda0d779133f7c04cc30a9a0427d58ae7da76d2e'),
        ('1207482', '1522744'), ('5a1acaa0c35e484c979401e3b6dfb36a', '293d218b06454bd1a8ff350bb93de2d5'),
        ('87863', '104329'), ('86264628081', '103062293730'),
        ('0.1.0-PG600', '0.1.0-PG631'),
        ('a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f', MANIFEST),
        ('pg609-completed-readonly-v1', 'pg640-completed-readonly-v1'),
        ('PG609-completed-readonly-v1', 'PG640-completed-readonly-v1'),
    ]
    for old, new in bindings:
        assert old in value
        value = value.replace(old, new)
    bounded = "require(datetime.datetime.fromisoformat(baseline['bounds']['lower'])<=datetime.datetime.fromisoformat(cutoff.replace('Z','+00:00'))<=datetime.datetime.fromisoformat(baseline['bounds']['upper']))"
    assert value.count(bounded) == 1
    value = value.replace(bounded, "require(cutoff=='2026-10-08T18:32:42.140966Z')")
    value = value.replace("activation=matches[0];done_path=", "activation=matches[0];require(activation=='7d381b67-b37b-48c6-99ac-e04a336f887d');done_path=")
    marker = "'wholeFormalAccepted':False}))"
    assert value.count(marker) == 1
    value = value.replace(marker, "'wholeFormalAccepted':False,'ownedUnits':{u:{k:v[k]for k in ('MainPID','InvocationID','ExecMainStartTimestampMonotonic','ActiveState','SubState')}for u,v in after['units'].items()},'parentEndedUTC':done.decode('ascii').splitlines()[4]}))")
    marker = 'require(0<len(raw)<=limit and p.lstat()==s)'
    assert value.count(marker) == 1
    value = value.replace(marker, 'require(0<len(raw)<=limit and metadata9(p.lstat())==metadata9(s) and not os.listxattr(p))')
    value = value.replace('def strict(p,limit):', 'def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)\ndef strict(p,limit):')
    assert "baseline['bounds']" not in value
    return value


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg638-observer-v1.exit').read_bytes() == b'0\n'
    observed = [json.loads(line) for line in (W/'pg638-watch-private-v1.jsonl').read_text().splitlines()]
    terminal = observed[-1]
    assert terminal['terminalObserved'] and terminal['parentExit'] == '0' and terminal['parentResult'] == 'success'
    assert set(terminal['readyObserved']) == set(terminal['rootsCaptured']) == {'api', 'web'} and terminal['caddyTlsLogin200']
    assert (W/'pg639-post-v2.exit').read_bytes() == b'0\n'
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    code = 'RECEIPT='+repr((R/'pg609_parent_receipt.py').read_text())+'\n'+payload()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=code.encode(), capture_output=True, timeout=90)
    with (W/'pg640-completed-readonly-v1.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with (W/'pg640-completed-readonly-v1.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        safe.update(startedUTC=started, endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        safe['operatorSource'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        with (W/'pg640-completed-readonly-v1.safe.json').open('x') as f: json.dump(safe, f, sort_keys=True)
        print(json.dumps(safe))
    else:
        print(json.dumps({'actualExit': result.returncode,
                          'privateLogSha256': hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
