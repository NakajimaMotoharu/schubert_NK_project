"""Independent current stop seal and fresh full postcondition, no Production imports/actions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg642_stop_binding import bindings
import pg613_terminal_final as previous

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
SEAL = r'''
import hashlib,json,os,pathlib,stat
assert os.geteuid()==0
def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg642-native-stop-v1');v={}
for name in ('before.private.json','after.private.json','parent.private.jsonl','complete.private'):
 p=r/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(p)and 0<s.st_size<=67108864
 raw=p.read_bytes();assert metadata9(p.lstat())==metadata9(s)and not os.listxattr(p);v[name]=hashlib.sha256(raw).hexdigest()
print(json.dumps(v))
'''


def payload(proof, seals):
    value = previous.PAYLOAD
    for old, new in bindings(proof): value = value.replace(old, new)
    for old, new in (
        ('pg613-terminal-final-v1', 'pg643-terminal-final-v2'), ('PG613-terminal-final-v1', 'PG643-terminal-final-v2'), ('pg600-manifest.sig', 'pg631-manifest.sig'),
        ('19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912', seals['before.private.json']),
        ('a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849', seals['after.private.json']),
        ('8f31ba931b056ae9776855ac503403e9688eb34316873169eb20205aae3badae', seals['complete.private']),
        ('fbc7033f0d6fd6b6ccd6de656882e2405dc42623b959a69ee86a6074d38e465e', seals['parent.private.jsonl']),
    ):
        assert old in value
        value = value.replace(old, new)
    marker = "require(p.lstat()==s and hashlib.sha256(raw).hexdigest()==sha)"
    assert value.count(marker) == 1
    value = value.replace(marker, "require(metadata9(p.lstat())==metadata9(s) and not os.listxattr(p) and hashlib.sha256(raw).hexdigest()==sha)")
    value = value.replace('def sealed(name,sha):', 'def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)\ndef sealed(name,sha):')
    return value


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg642-native-stop-v1.exit').read_bytes() == b'0\n'
    proof = json.loads((W/'pg640-completed-readonly-v1.safe.json').read_bytes())
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    seals = json.loads(subprocess.check_output(ssh, input=SEAL.encode(), timeout=20))
    build = json.loads((W/'pg642-native-build-v1.safe.json').read_bytes())
    names = ('Pg642NativeStop.class', 'Pg642NativeStop$References.class', 'pg642_native_refs.py',
             'pg642_native_owned_stop.py', 'pg526_term_witness.py', 'pg526_native_term_witness.py',
             'pg642_parent_receipt.py', 'pg642_durable.py')
    hashes = {name: build['files'][name] for name in names}
    receipt = (W/'pg642-native-tools-v1/pg642_parent_receipt.py').read_text()
    code = 'HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload(proof, seals)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=code.encode(), capture_output=True, timeout=90)
    with (W/'pg643-terminal-final-v2.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with (W/'pg643-terminal-final-v2.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        safe.update(startedUTC=started, endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    operatorSource=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
        with (W/'pg643-terminal-final-v2.safe.json').open('x') as f: json.dump(safe, f, sort_keys=True)
        print(json.dumps({k:safe[k] for k in ('actualExit', 'run', 'all24UnchangedTwice', 'allTenUnitsKernelEmpty', 'allActorGone', 'allClientAdvisoryFlock0', 'whole187SignedArtifactBytesVerified', 'nativePhysicalFiles')}))
    else: print(json.dumps({'actualExit': result.returncode, 'privateLogSha256': hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
