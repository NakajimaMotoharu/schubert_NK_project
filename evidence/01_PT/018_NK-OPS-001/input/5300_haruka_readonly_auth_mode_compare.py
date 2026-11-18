"""Compare saved haruka connection options without opening any SSH connection."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
CURRENT = Path(__file__).with_name('5296_haruka_filestore_precheck.py')
OLD = Path(__file__).with_name('2558_haruka_readonly_eligibility_after_legitimate_repair.py')


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def main():
    plan = json.loads(next(D.glob('640_haruka*')).read_bytes())['values']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == plan['source']
    assert all(ref(r['path']) == r for r in plan['oracleReferences'])
    failed, older, recent = (json.loads(Path(r['path']).read_bytes()) for r in plan['oracleReferences'])
    assert failed['actualExit'] == 255 and failed['observed'] is None
    assert older['actualExit'] == 0 and older['sshAuthPrompts'] == 1
    assert failed['knownHostsSha256'] == older['knownHostsSha256']
    assert older['strictPinnedPeer'] and not older['authSecretExported']
    earlier_code = OLD.read_text()
    assert 'NumberOfPasswordPrompts=1' in earlier_code and 'c.sendline(cfg[' in earlier_code
    command = runpy.run_path(str(CURRENT))['ssh_args']()
    # OpenSSH -G prints the local effective settings and exits before connecting.
    inspected = subprocess.run([command[0], '-G', *command[1:]], capture_output=True, timeout=8, check=True)
    config = {}
    for line in inspected.stdout.decode().splitlines():
        name, _, value = line.partition(' ')
        config.setdefault(name, []).append(value)
    assert config['batchmode'] == ['yes'] and config['stricthostkeychecking'] == ['true']
    assert config['user'] == ['mini']
    candidates = [Path(entry).expanduser() for entry in config.get('identityfile', ())]
    assert all(p.is_absolute() for p in candidates)
    available = sum(p.is_file() for p in candidates)
    a = subprocess.run(['/usr/bin/ssh-add', '-l'], capture_output=True, timeout=8, check=False)
    no_agent_id = a.returncode == 1 and b'no identities' in (a.stdout + a.stderr).lower()
    assert recent['harukaOwnerCheck'] == 'Authenticated mini via existing pinned SSH host key'
    record = dict(
        actualExit=0, source=plan['source'], oldPinSame=True,
        pastSuccess=dict(exit=older['actualExit'], promptCount=older['sshAuthPrompts'],
                         method='One password prompt in existing fixed-key harness'),
        failedRun=dict(exit=failed['actualExit'], rawAuthenticationDiagnosticAvailable=False,
                       options=dict(batchMode=True, customSshConfigDisabled=True, pinnedHostKey=True)),
        freshLocalOnly=dict(candidateIdentityFileCount=len(candidates), candidateIdentityFilePresent=available,
                            agentConfigured=bool(os.environ.get('SSH_AUTH_SOCK')), agentExit=a.returncode,
                            agentReportsNoIdentities=no_agent_id, noSecretValueReadOrPublished=True),
        currentPmoSuccess=dict(ownerConfirmedInPmo=True, authenticationMethodRecorded=False,
                               freeBytes=recent['haruka']['freeUserBytes']),
        finding='Failed invocation does not reproduce the previously recorded prompt-capable authenticated mode.',
        exactCause='UNDETERMINED_WITHOUT_ORIGINAL_AUTH_DIAGNOSTIC',
        storageCauseEstablished=False, harukaNetworkAttempts=0, gateCliExecuted=False,
        ioriPolicy='Overflow for completed restorable run artifacts only if approved haruka space is insufficient.',
        ioriUsed=False, productTests=0, newFormalAcceptance=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), inputs=plan['oracleReferences'])
    out = E / plan['run']
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(record, indent=2) + '\n')
    print(ref(p), record['freshLocalOnly'])


if __name__ == '__main__':
    main()
