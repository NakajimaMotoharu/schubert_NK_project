"""One pidfd TERM to authenticated fixture forward parent, no primary signal."""
import hashlib
import json
import os
import select
import signal
import subprocess
from pg3212_legacy_negative_forward import fingerprint, OUT as FORWARD
from pg1446_current_cold_stage import W

OUT = W / 'pg3242-negative-fixture-forward-close-v1'


def qualify(post, fixed, parent, child):
    if (post.get('actualExit') != 0 or post.get('fixtureQemuGone') is not True or post.get('fixtureDiskNoOpeners') is not True
            or post.get('primaryUntouched') is not True or fixed.get('port') != 22224 or fixed.get('guestKeyTransferred') is not False
            or parent != fixed.get('parent') or child != fixed.get('child') or parent['pid'] == child['pid']
            or child['ppid'] != parent['pid'] or child['exe'] != '/usr/bin/ssh'):
        raise ValueError('exact owned fixture forward normal-close contract refused')


def main():
    os.umask(0o077)
    post = json.loads((W / 'pg3240-negative-fixture-poweroff-v1/server-post.safe.json').read_text())
    fixed = json.loads((FORWARD / 'running.safe.json').read_text())
    parent = fingerprint(fixed['parent']['pid']); child = fingerprint(fixed['child']['pid'])
    qualify(post, fixed, parent, child)
    OUT.mkdir(mode=0o700)
    with (OUT / 'reservation.safe.json').open('x') as file:
        json.dump({'issuedOnce': True, 'parent': parent, 'child': child, 'VMAlreadyDown': True, 'primaryOperations': 0}, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    fd = os.pidfd_open(parent['pid'])
    try:
        qualify(post, fixed, fingerprint(parent['pid']), fingerprint(child['pid']))
        poll = select.poll(); poll.register(fd, select.POLLIN)
        signal.pidfd_send_signal(fd, signal.SIGTERM)
        if not poll.poll(15000): raise ValueError('owned forward close pending; no repeat or force')
    finally: os.close(fd)
    raw = (FORWARD / 'closed.safe.json').read_bytes(); closed = json.loads(raw)
    if not closed['ownedChildExited'] or not closed['operatorStop'] or not closed['listener22224Absent'] or closed['guestOperations'] != 0:
        raise ValueError('normal forward tool terminal required')
    if subprocess.check_output(['ss', '-H', '-lnt', '( sport = :22224 )']): raise ValueError('fixture listener remains')
    value = {'actualExit': 0, 'normalPidfdTermOnce': True, 'parentPid': parent['pid'], 'childPid': child['pid'], 'ownedChildTerminal': closed,
             'closedReceiptSha256': hashlib.sha256(raw).hexdigest(), 'fixtureListenerGone': True, 'primaryOperations': 0, 'formalAccepted': False}
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value), flush=True)


if __name__ == '__main__':
    main()
