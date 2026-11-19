"""Authorize and collect one bounded GateCli run over the approved ordinary haruka SSH route."""
from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
import io
import json
import shlex
import subprocess
import sys
import tarfile

import pexpect

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
PMO = Path('../PMO/hourly-monitor').resolve()
sys.path.insert(0, str(PMO / 'haruka-transition-20261114'))
from remote_access import config

HERE = Path(__file__)
RUNNER = HERE.with_name('5310_haruka_filestore_owned_runner.py')
RUN = 'PG40160-p020-haruka-real-filestore-v1'
MIN_BYTES = 20 * 1024**3
WORK = '/home/mini/schubert-nk-pgpt/validation-work'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(p):
    return dict(path=str(p), sha256=sha(Path(p).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def now():
    return datetime.now(timezone.utc).isoformat()


def capsule(prep, head):
    archive = Path(prep['archive']['path'])
    assert ref(archive) == prep['archive']
    files = {}
    with tarfile.open(archive, 'r:') as source:
        for entry in source.getmembers():
            path = entry.name
            assert entry.isfile() and entry.name.startswith('program/characterization/src/main/java/')
            data = source.extractfile(entry).read()
            assert sha(data) == prep['sourceHashes'][path]
            assert git('show', f'{head}:{path}') == data and path not in files
            files[path] = data
    assert files.keys() == prep['sourceHashes'].keys() and len(files) == 6
    for name, pin in prep['exactLocalTools'].items():
        assert Path(name).name == name and name.endswith('.jar')
        data = Path(pin['path']).read_bytes()
        assert sha(data) == pin['sha256']
        files['sdk/' + name] = data
    assert len(files) == 13
    portable = io.BytesIO()
    with tarfile.open(fileobj=portable, mode='w:', format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(files.items()):
            row = tarfile.TarInfo(name)
            row.size = len(data)
            row.mode = 0o600
            archive.addfile(row, io.BytesIO(data))
    return portable.getvalue(), {name: sha(data) for name, data in files.items()}


def ssh_options(cfg, pinned):
    assert pinned.is_file()
    host = cfg['addr']
    key = subprocess.run(['/usr/bin/ssh-keygen', '-F', host, '-f', str(pinned)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    assert key.returncode == 0
    return ['-T', '-F', '/dev/null', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'UserKnownHostsFile=' + str(pinned), '-o', 'GlobalKnownHostsFile=/dev/null',
            '-o', 'UpdateHostKeys=no', '-o', 'ForwardAgent=no', '-o', 'ClearAllForwardings=yes',
            '-o', 'ControlMaster=no', '-o', 'ConnectTimeout=12',
            '-o', 'BatchMode=no', '-o', 'PreferredAuthentications=password',
            '-o', 'NumberOfPasswordPrompts=1', 'mini@' + host]


def main():
    start = json.loads(next(D.glob('659_P020*')).read_bytes())['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == start['source'] and start['run'] == RUN
    pin = start['oracleReferences'][0]
    assert ref(pin['path']) == pin
    prep = json.loads(Path(pin['path']).read_bytes())
    assert prep['productionCore'] == start['productionCoreMain'] and len(prep['mainPhysical']) == 17
    assert prep['localCompileExit'] == 0 and not prep['byteDifferencesVs206']
    payload, hashes = capsule(prep, head)
    assert 0 < len(payload) < 7 * 1024**2
    spec = dict(capsuleSha256=sha(payload), size=len(payload), files=hashes, classHashes=prep['mainPhysical'],
                java=prep['java']['sha256'], javac=prep['javac']['sha256'])
    code = RUNNER.read_bytes() + ('\nrun(' + repr(spec) + ')\n').encode()
    remote = 'python3 -u -c ' + shlex.quote('import base64;exec(base64.b64decode(' + repr(base64.b64encode(code).decode()) + '))')
    cfg = config('haruka')
    pinned = PMO / 'haruka_known_hosts'
    route = ssh_options(cfg, pinned)
    target = E / RUN
    target.mkdir()
    begin = dict(source=head, productionCore=prep['productionCore'], priorToolSource=prep['priorToolSource'],
                 group=start['contextGroupId'], pinnedKnownHostsSha256=ref(pinned)['sha256'],
                 program='PT-CHR-PREFLIGHT-FS-001', input=pin, runner=ref(RUNNER),
                 capsule={k:v for k,v in spec.items() if k!='classHashes'}, startedAtUTC=now(),
                 ordinaryPasswordPromptLimit=1, backendOperationsPermitted=0)
    (target/'begin.json').write_text(json.dumps(begin, indent=2)+'\n')
    child = pexpect.spawn('/usr/bin/ssh', [*route, remote], encoding=None, timeout=90, echo=False)
    prompts = 0
    admitted = None
    terminal = None
    sent = False
    mode = 'UNOBSERVED'
    normalized = b''
    try:
        while True:
            case = child.expect([rb'(?i)password(?: for [^:\r\n]+)?:',
                                 rb'HARUKA_READY ([^\r\n]+)\r?\n',
                                 rb'HARUKA_TERMINAL ([^\r\n]+)\r?\n', pexpect.EOF, pexpect.TIMEOUT])
            normalized += child.before[-1024:]
            if case == 0:
                prompts += 1
                if prompts > 1 or admitted is not None:
                    mode = 'AUTHENTICATION_PROMPT_REFUSED'
                    break
                child.sendline(cfg['users']['mini'].encode())
            elif case == 1:
                assert admitted is None and not sent and prompts == 1
                admission = json.loads(child.match.group(1))
                assert admission['host'] == 'haruka' and admission['uid'] == 1000
                assert admission['workspace'] == WORK and admission['workspaceMode'] == '0700'
                assert admission['activeOwnedWorkspaceJobs'] == 0 and admission['runAbsent']
                assert admission['freeBytes'] >= MIN_BYTES and admission['boot']
                admitted = admission
                (target/'admission.json').write_text(json.dumps(admitted, indent=2)+'\n')
                child.delaybeforesend = 0
                data = base64.b64encode(payload)
                for offset in range(0, len(data), 1800):
                    chunk = data[offset:offset+1800] + b'\n'
                    assert child.send(chunk) == len(chunk)
                child.sendline(b'PAYLOAD-END')
                sent = True
            elif case == 2:
                assert terminal is None
                terminal = json.loads(child.match.group(1))
            elif case == 3:
                mode = 'TERMINAL_RETURNED' if terminal is not None else 'NO_OWNED_TERMINAL'
                break
            else:
                mode = 'UNKNOWN_TIMEOUT_NO_RETRY'
                break
    except (AssertionError, pexpect.ExceptionPexpect, OSError, ValueError) as error:
        mode = 'LOCAL_FAILURE_NO_RETRY_' + type(error).__name__
    finally:
        child.close(force=child.isalive())
    if b'Permission denied' in normalized:
        mode = 'AUTHENTICATION_OR_OS_PERMISSION_DENIED_NO_RETRY'
    if b'Host key verification failed' in normalized:
        mode = 'PINNED_HOST_KEY_REJECTED_NO_RETRY'
    succeeded = terminal is not None and child.exitstatus == 0 and terminal['actualExit'] == 0
    qualification = {}
    if succeeded:
        assert terminal['boot'] == admitted['boot'] and terminal['ownerUid'] == admitted['uid']
        assert terminal['physical'] == prep['mainPhysical']
        assert terminal['workspace'] == WORK + '/' + RUN
        for name, row in terminal.pop('payloads').items():
            assert name in ('preflight.json', 'file-store.exec', 'coverage.xml')
            data = base64.b64decode(row['data'], validate=True)
            assert sha(data) == row['sha256']
            f = target / name
            f.write_bytes(data)
            qualification[name] = ref(f)
        assert qualification.keys() == {'preflight.json', 'file-store.exec', 'coverage.xml'}
    value = dict(actualExit=0 if succeeded else 1, source=head, productionCore=prep['productionCore'],
                 toolSource=prep['priorToolSource'], sshExit=child.exitstatus, sshSignal=child.signalstatus,
                 authPrompts=prompts, outcome=mode, admission=admitted, capsuleSent=sent,
                 terminal=terminal, artifacts=qualification, rawAuthOutputSaved=False,
                 remoteWorkspaceRetained=True if sent else None, terminalAtUTC=now(),
                 newFormalAcceptance=0, whole451Accepted=False)
    file = target/'manifest.json'
    file.write_text(json.dumps(value, indent=2)+'\n')
    print(dict(actualExit=value['actualExit'], sshExit=child.exitstatus, mode=mode,
               admitted=admitted is not None, trueTerminal=terminal is not None, evidence=ref(file)))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
