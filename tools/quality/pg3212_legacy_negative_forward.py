"""Owned new22224 management tunnel only; normal pidfd TERM, no guest operation."""
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time
import pexpect
from lan_server import HOST, pinned_key, credentials, ssh_options
from pg1446_current_cold_stage import P

OUT = P / 'pg3212-legacy-negative-forward-v1'


def fingerprint(pid):
    p = Path('/proc') / str(pid)
    first = (p / 'stat').read_text().rpartition(')')[2].split()
    argv = (p / 'cmdline').read_bytes()
    value = {'pid': pid, 'ticks': int(first[19]), 'ppid': int(first[1]), 'argvSha256': hashlib.sha256(argv).hexdigest(), 'exe': str((p / 'exe').readlink())}
    if first[19] != (p / 'stat').read_text().rpartition(')')[2].split()[19] or argv != (p / 'cmdline').read_bytes():
        raise ValueError('owned tunnel identity unstable')
    return value


def save(name, value):
    with (OUT / name).open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def main():
    os.umask(0o077)
    if subprocess.check_output(['ss', '-H', '-lnt', '( sport = :22224 )']):
        raise ValueError('existing fixture forward never replaced')
    key = pinned_key(); OUT.mkdir(mode=0o700)
    known = OUT / 'known_hosts.public'
    with known.open('x') as file:
        file.write(key + '\n'); file.flush(); os.fsync(file.fileno())
    args = ['-N', '-T', *ssh_options(known), '-o', 'ExitOnForwardFailure=yes',
            '-L', '127.0.0.1:22224:127.0.0.1:22224', f'mini@{HOST}']
    save('reservation.safe.json', {'parent': fingerprint(os.getpid()), 'purpose': 'NEW_ONLY_FIXTURE_MANAGEMENT_FORWARD', 'port': 22224, 'argvSha256': hashlib.sha256(b'\0'.join(v.encode() for v in ['ssh', *args]) + b'\0').hexdigest(), 'guestOperations': 0})
    child = pexpect.spawn('ssh', args, encoding='utf-8', timeout=20, echo=False)
    # exec may still be changing argv immediately after pexpect.spawn. Record
    # allocation provenance, not an unearned authenticated SSH fingerprint.
    allocated = (Path('/proc') / str(child.pid) / 'stat').read_text().rpartition(')')[2].split()
    save('spawned.safe.json', {'pid': child.pid, 'ticks': int(allocated[19]), 'ppid': int(allocated[1]), 'authenticationCompleted': False, 'guestOperations': 0})
    stopping = False
    def stop(_signal, _frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    child.expect(r'(?i)password:'); child.sendline(credentials())
    for _ in range(100):
        if not child.isalive():
            raise ValueError('new tunnel exited; never auto restart')
        if subprocess.check_output(['ss', '-H', '-lnt', '( sport = :22224 )']):
            break
        time.sleep(.1)
    else:
        raise ValueError('new tunnel not ready; preserve without retry')
    owner = fingerprint(child.pid)
    if owner['ppid'] != os.getpid() or owner['exe'] != '/usr/bin/ssh':
        raise ValueError('actual owned SSH child required')
    save('running.safe.json', {'parent': fingerprint(os.getpid()), 'child': owner, 'port': 22224, 'miniOnly': True, 'guestKeyTransferred': False, 'guestIdentityNotYetQualified': True})
    print('PG3212_OWNED_FORWARD_READY port22224=true guestUnqualified=true', flush=True)
    while not stopping and child.isalive():
        time.sleep(1)
    if child.isalive():
        fd = os.pidfd_open(child.pid)
        try:
            if fingerprint(child.pid) != owner:
                raise ValueError('tunnel child changed; no signal')
            wait = select.poll(); wait.register(fd, select.POLLIN)
            signal.pidfd_send_signal(fd, signal.SIGTERM)
            if not wait.poll(10000):
                raise ValueError('owned SSH TERM pending; no force or repeated signal')
        finally:
            os.close(fd)
    child.expect(pexpect.EOF, timeout=10); child.close(force=False)
    if subprocess.check_output(['ss', '-H', '-lnt', '( sport = :22224 )']):
        raise ValueError('fixture listener remains; preserve')
    save('closed.safe.json', {'ownedChildExited': True, 'operatorStop': stopping, 'listener22224Absent': True, 'actualExit': child.exitstatus, 'signal': child.signalstatus, 'guestOperations': 0})


if __name__ == '__main__':
    main()
