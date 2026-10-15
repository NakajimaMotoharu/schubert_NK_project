"""Separate actual PID1 mount-namespace RO and full current/candidate resource post."""
import hashlib
import json
import os
import subprocess

from pyflakes.api import check
import pg3440_current_outbox_unused_post as previous
import pg3442_current_outbox_ro_sources as role
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

SLOT = 'pg3448-current-outbox-ro-independent-post-v1'


def payload():
    raw = previous.payload().replace(previous.SLOT, SLOT).replace(role.role.SAVE, role.SAVE)
    raw = raw.replace('unusedCandidatePlaced=true', 'candidateReadOnlyVerified=true')
    marker = "save=base/'" + SLOT + "'"
    if raw.count(marker) != 1:
        raise ValueError('one full independent RO post save boundary')
    extra = """require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG3420'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    raw = raw.replace(marker, extra + marker).replace("'unusedCandidate187Verified':True",
                                                     "'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    if check(raw, '<whole independent current/candidate RO post>'):
        raise ValueError('whole RO namespace required')
    compile(raw, '<currenta9 candidate4856 full RO post>', 'exec')
    return raw


def main():
    actual = json.loads((W / 'pg3446-prepare-ro-v1.safe.json').read_bytes())
    if (actual['actualExit'] != 0 or actual['candidateSource'] != role.role.SOURCE
            or actual['sourceQualified'] is not True or actual['currentApprovalEpochChanged'] is not False):
        raise ValueError('genuine owned current candidate RO terminal required')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean independent RO observer')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir()
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    with management_gate(P / 'current-management-critical.lock'):
        result = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw,
                                capture_output=True, timeout=120)
    (out / 'stderr.private.log').write_bytes(result.stderr)
    value = {'actualExit': result.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(),
             'formalAccepted': False}
    if result.returncode == 0:
        value['guest'] = json.loads(result.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
