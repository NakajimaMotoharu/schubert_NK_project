"""SSC305 fixed failed-phase read-only entry; ordinary management gate stays held."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, SSH, P
from pg4996_resume_connection import authenticate_host
import pg5092_retained_pair_full_proof as proof

SLOT = 'pg5094-failed-phase-full-proof-v1'


def host_owner(path):
    p = Path('/proc/46551')
    state = (p / 'stat').read_text().rpartition(')')[2].split()
    if (int(state[19]) != 981997 or int(state[1]) != 5960
            or os.readlink(p / 'exe') != '/usr/bin/python3.14'
            or hashlib.sha256((p / 'cmdline').read_bytes()).hexdigest() != 'b441bbc8991285b9c0d35dd928fb87edb7b50732bfbfdc8cb3571487cfe4c91b'
            or Path('/proc/sys/kernel/random/boot_id').read_text().strip() != '8cffa9ef-eaef-485d-828f-eb2e82da0497'):
        raise ValueError('same current failed wrapper generation required')
    s, f = path.lstat(), (p / 'fd/4').stat()
    if (not stat.S_ISREG(s.st_mode) or (s.st_uid, stat.S_IMODE(s.st_mode), s.st_nlink) != (os.geteuid(), 0o600, 1)
            or os.listxattr(path) or (s.st_dev, s.st_ino) != (66306, 9337730)
            or (s.st_dev, s.st_ino) != (f.st_dev, f.st_ino)):
        raise ValueError('same private retained gate fd4 required')
    hits = [v for line in Path('/proc/locks').read_text().splitlines()
            if len(v := line.split()) >= 8 and v[1] == 'FLOCK'
            and v[5] == f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}']
    if len(hits) != 1 or hits[0][1:5] != ['FLOCK', 'ADVISORY', 'WRITE', '46551']:
        raise ValueError('sole original failed wrapper must retain exclusion')
    return True


def fixed_failure():
    path = W / 'pg5086-current-bootstrap-verify-v1.private.log'
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid() or s.st_nlink != 1 or s.st_size != 822:
        raise ValueError('immutable actual failure log first')
    raw = path.read_bytes()
    if ((W / 'pg5086-current-bootstrap-verify-v1.exit').exists()
            or b'PG5082_BOOTSTRAP_RETIRE_UNKNOWN phase=PREPARE_DATABASE_SCOPE type=java.lang.IllegalStateException ownershipRetained=true oldCloseNotInferred=true\n' not in raw
            or b'PG5082_BOOTSTRAP_RETIRE_FRAME method=lambda$main$4 line=100\n' not in raw
            or b'PG5082_DB_NOT_CONFIRMED ownershipNotInferred=true\n' not in raw):
        raise ValueError('fixed failed-phase only, no general critical diagnostic')
    return True


def payload():
    return proof.payload().replace('SLOT=' + repr(proof.SLOT), 'SLOT=' + repr(SLOT), 1)


def main():
    fixed_failure()
    host_owner(P / 'current-management-critical.lock')
    authenticate_host()
    raw = payload()
    if check(raw, '<SSC305 fixed failed-phase readonly complete namespace>'):
        raise ValueError('complete failed-phase namespace required')
    compile(raw, '<same frozen failed phase only>', 'exec')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    (out / 'payload.private.py').write_text(raw)
    # Explicit SSC305 failed-phase diagnostic exception, not a general management
    # gate override: exact old host owner is authenticated before AND after read.
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=180)
    for name, blob in [('stdout.private.log', r.stdout), ('stderr.private.log', r.stderr)]:
        with (out / name).open('xb') as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
    value = {'actualExit': r.returncode, 'source': proof.role.SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'observedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'signals0': True, 'formalAccepted': False}
    host_owner(P / 'current-management-critical.lock')
    if r.returncode == 0:
        value['result'] = json.loads(r.stdout)
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
