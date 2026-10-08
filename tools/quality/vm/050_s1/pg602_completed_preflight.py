"""Fresh post-stage readonly old genuine-DONE and unused-candidate proof; no activation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg580_terminal_final as baseline

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    # One closed saved proof path and result label only; actual original checks are unchanged.
    source = baseline.PAYLOAD
    old = "save=base/'pg580-terminal-final-v1'"
    assert source.count(old) == 1
    source = source.replace(old, "save=base/'pg602-completed-preflight-v1'")
    old = "'run':'PG580-terminal-final-v1'"
    assert source.count(old) == 1
    source = source.replace(old, "'run':'PG602-completed-preflight-v1'")
    anchor = "bus=dbus.SystemBus(private=True);"
    assert source.count(anchor) == 1
    candidate = r'''
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG600')
candidate_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(candidate_raw).hexdigest()=='a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f')
candidate_data=json.loads(candidate_raw)
require(candidate_data['source']['commit']=='23b14a44b10504172e030bbd6625926bf049fb5c'and len(candidate_data['artifacts'])==187 and candidate_data['versions']['schema']=='028')
expected={v['path']for v in candidate_data['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'}
require({p.relative_to(candidate).as_posix()for p in candidate.rglob('*')if p.is_file()}==expected)
for p in(candidate,*candidate.rglob('*')):
 s=p.lstat();executable=p.relative_to(candidate).as_posix()in('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 require(not p.is_symlink()and s.st_uid==0 and s.st_gid==986 and stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640))
 if p.is_file():require(stat.S_ISREG(s.st_mode)and s.st_nlink==1)
for v in candidate_data['artifacts']:
 p=candidate/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg600-manifest.sig')],4096)
'''
    source = source.replace(anchor, candidate + '\n' + anchor)
    marker = "'formalAccepted':False}"
    assert source.count(marker) == 1
    source = source.replace(marker, "'formalAccepted':False,'candidateWhole187SignatureVerified':True,'candidateSource':'23b14a44b10504172e030bbd6625926bf049fb5c','candidateManifestSha256':'a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f','activationNotRun':True}")
    compile(source, '<fixed fresh completed preflight>', 'exec')
    return source


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R.parents[3], text=True).strip()
    assert (W / 'pg601-candidate-stage-v1.safe.json').is_file()
    stage = json.loads((W / 'pg601-candidate-stage-v1.safe.json').read_bytes())
    assert stage['actualExit'] == 0 and stage['currentUnchanged']
    log = W / 'pg602-completed-preflight-v1.private.log'
    assert not log.exists() and not (W / 'pg602-completed-preflight-v1.safe.json').exists()
    classes = W / 'pg579-native-tools-v1'
    files = {n: classes / n for n in ('Pg579NativeStop.class', 'Pg579NativeStop$References.class')}
    for n in ('pg579_native_refs.py', 'pg579_native_owned_stop.py', 'pg526_term_witness.py',
              'pg526_native_term_witness.py', 'pg579_parent_receipt.py', 'pg579_durable.py'):
        files[n] = R / n
    hashes = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in files.items()}
    prefix = 'HASHES=' + repr(hashes) + '\nRECEIPT=' + repr((R / 'pg579_parent_receipt.py').read_text()) + '\n'
    code = prefix + payload()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    result = subprocess.run(ssh, input=code.encode(), capture_output=True, timeout=90)
    with log.open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    safe = {'actualExit': result.returncode, 'operatorSource': operator, 'startedUTC': started,
            'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(),
            'payloadSha256': hashlib.sha256(code.encode()).hexdigest(), 'formalAccepted': False}
    if result.returncode == 0:
        proof = json.loads(result.stdout)
        assert proof['run'] == 'PG602-completed-preflight-v1' and proof['candidateWhole187SignatureVerified']
        safe['proof'] = proof
    with (W / 'pg602-completed-preflight-v1.safe.json').open('x') as f:
        json.dump(safe, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': result.returncode, 'currentUnchanged': result.returncode == 0,
                      'allOriginalBackupDbUnitValuesRechecked': result.returncode == 0,
                      'activationNotRun': True, 'formalAccepted': False}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
