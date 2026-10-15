"""Fresh seven-case cohort after BUG1274, retain exact Unit terminal then stop.

Only fixed isolated boot; no old failed native import, ordinary business or key
transfer. Reuses independently fixed runtime Main bytes, never old case success.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import pg3216_legacy_negative_observer as observer

BASE = observer.BASE
OUT = BASE / 'observer-cohort-v2'
DROP = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3218-negative-fixture.conf')
CASE_NAME = 'case-cohort-v2'
NATIVE_NAME = 'cohort-native-v2.exec'
SESSION_ID = 'PG3218-LFACT-v2'


def runtime_fixed():
    setup = json.loads((BASE / 'setup.safe.json').read_text())
    root = BASE / 'runtime'; meta_file = root / 'input.safe.json'
    observer.require(observer.sha(meta_file) == setup['inputSha256'])
    meta = json.loads(meta_file.read_text())
    observer.require(meta['loadedMainSource'] == observer.SOURCE and meta['allMainSameBytes'] == 1643 and meta['hostTests'] == 3694)
    observer.require({str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == set(meta['files']) | {'input.safe.json'})
    for name, expected in meta['files'].items():
        p = root / name; s = p.lstat()
        observer.require(stat.S_ISREG(s.st_mode) and s.st_uid == s.st_gid == 0 and stat.S_IMODE(s.st_mode) == 0o400 and s.st_nlink == 1
                         and s.st_size == expected['bytes'] and observer.sha(p) == expected['sha256'])


def prepare():
    observer.guard(); require = observer.require
    require(not OUT.exists() and not DROP.exists())
    old = json.loads((BASE / 'failed.safe.json').read_text())
    require(old == {'actualExit': 1, 'casesPassed': 7, 'nativeAccepted': False, 'type': 'ValueError'})
    u = observer.unit(); require(u['MainPID'] == u['ControlPID'] == '0' and u['Job'] == '' and u['ActiveState'] == 'inactive')
    original = json.loads((BASE / 'setup.safe.json').read_text())
    require(original['boot'] == observer.BOOT and original['source'] == observer.SOURCE and original['actualExit'] == 0)
    old_drop = observer.DROP; require(observer.sha(old_drop) == original['unitDropinSha256'])
    require(observer.sha(BASE / 'original-approval.private') == observer.ORIGINAL_APPROVAL)
    observer.stable_bad()
    runtime_fixed()
    # Remove only our closed observer's exact stale socket, never any listener.
    sock = observer.RUN / 'watch.sock'; s = sock.lstat()
    require(stat.S_ISSOCK(s.st_mode) and s.st_uid == s.st_gid == 0 and stat.S_IMODE(s.st_mode) == 0o600)
    require(str(sock) not in Path('/proc/net/unix').read_text())
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
        try: probe.connect(str(sock))
        except ConnectionRefusedError: pass
        else: raise ValueError('old observer still listening; no mutation')
    require(sock.lstat() == s); sock.unlink()
    OUT.mkdir(mode=0o700)
    # The formerly failed cohort is immutable history. Only destination and
    # RemainAfterExit differ; no new Production artifact or source compilation.
    text = old_drop.read_text()
    require(text.count('case-cohort-v1') == text.count('cohort-native.exec') == text.count('sessionid=PG3216-LFACT-v1') == 1)
    text = text.replace('case-cohort-v1', CASE_NAME).replace('cohort-native.exec', NATIVE_NAME).replace('sessionid=PG3216-LFACT-v1', 'sessionid=' + SESSION_ID)
    text += 'RemainAfterExit=yes\n'
    with DROP.open('x') as file:
        file.write(text); file.flush(); os.fsync(file.fileno())
    DROP.chmod(0o644)
    observer.command(['systemctl', 'daemon-reload'])
    observer.no_exit_hooks()  # Prove the live ABI before a case/Unit start is issued.
    proof = {'actualExit': 0, 'boot': observer.BOOT, 'source': observer.SOURCE, 'oldFailedWhole': 1, 'oldFailedNativeImported': False,
             'unitDropinSha256': hashlib.sha256(text.encode()).hexdigest(), 'originalRuntime': original, 'newCasesRun': 0, 'formalAccepted': False}
    with (OUT / 'setup.safe.json').open('x') as file:
        json.dump(proof, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def execute():
    observer.guard()
    runtime_fixed()
    proof = json.loads((OUT / 'setup.safe.json').read_text())
    observer.require(proof['actualExit'] == 0 and observer.sha(DROP) == proof['unitDropinSha256'])
    observer.RESULTS = OUT; observer.CASE = BASE / CASE_NAME
    observer.NATIVE = BASE / NATIVE_NAME; observer.RETAINED_TERMINAL = True
    observer.execute()


def retire_failed():
    observer.guard(); runtime_fixed(); require = observer.require
    proof = json.loads((OUT / 'setup.safe.json').read_text())
    require(observer.sha(DROP) == proof['unitDropinSha256'])
    require(json.loads((OUT / 'failed.safe.json').read_text()) == {'actualExit': 1, 'casesPassed': 7, 'nativeAccepted': False, 'type': 'ValueError'})
    before = json.loads((OUT / 'before.private.json').read_text())
    require(observer.tree() == before['tree'] and observer.database() == before['database'] and observer.stable_bad() == before['bad'])
    terminal = observer.unit(); observer.require_terminal(terminal, terminal['InvocationID'], True)
    require(len(terminal['InvocationID']) == 32)
    observer.no_exit_hooks()
    pid_text = observer.typed_service_property('ExecMainPID').split()
    require(len(pid_text) == 2 and pid_text[0] == 'u' and pid_text[1].isdigit() and int(pid_text[1]) > 1 and not Path('/proc', pid_text[1]).exists())
    group = Path('/sys/fs/cgroup/system.slice') / observer.UNIT
    require(not group.exists() or not (group / 'cgroup.procs').read_text().strip())
    observer.RESULTS = OUT
    observer.save('failed-owned-stop-reservation.safe.json', {'issuedOnce': True, 'invocation': terminal['InvocationID'], 'terminal': terminal, 'nativeAccepted': False})
    require(observer.unit() == terminal)
    observer.command(['systemctl', 'stop', observer.UNIT])
    post = observer.unit()
    require(post['ActiveState'] == 'inactive' and post['SubState'] == 'dead' and post['MainPID'] == post['ControlPID'] == '0' and post['Job'] == '')
    require(not group.exists() or not (group / 'cgroup.procs').read_text().strip())
    require(observer.tree() == before['tree'] and observer.database() == before['database'])
    observer.save('failed-owned-stop.safe.json', {'actualExit': 0, 'nativeAccepted': False, 'oldWholeActualExit': 1})


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['prepare', 'execute', 'retire-failed']); phase = parser.parse_args().phase
    {'prepare': prepare, 'execute': execute, 'retire-failed': retire_failed}[phase]()


if __name__ == '__main__':
    main()
