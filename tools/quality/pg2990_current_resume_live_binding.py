"""Read-only new Root identity, same completed run/cutoff and distinct activation."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg2982_current_resume_observer import SOURCE, BOM
from pg2362_current_resume_live_binding import body as previous

SLOT = 'pg2990-current-resume-live-binding-v1'


def body():
    raw = previous()
    for a, b in [('b2d6f605-61cf-425f-8fbd-12d606f6ee66', '79a3260a-e16d-42bf-942a-b914ed144c28'), ('b2d6f60561cf425f8fbd12d606f6ee66', '79a3260ae16d42bf942ab914ed144c28'), ('PG2126', 'PG2802'), ('91f5484b-9702-4c7c-97f3-dd5110a853f9', '0dc63b79-3f9a-450c-b2a6-56f86272d272'), ('2026-10-13T15:01:53.237266Z', '2026-10-14T19:12:28.842213Z'), ('9be93262-fbb2-438f-b2b0-c4a27f5563a4', '74729e17-91c0-43e7-b01f-74f9e6461d6a')]:
        raw = raw.replace(a, b)
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n' + raw, '<current distinct Root binding>'):
        raise ValueError('complete current binding namespace required')
    compile(raw, '<current distinct Root binding>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed read-only operator required')
    actual = json.loads((W / 'pg2984-current-fresh-resume-once-v1/manifest.safe.json').read_bytes())
    if actual['actualExit'] != 0 or actual['sourceQualified'] is not True or actual['productionSource'] != SOURCE:
        raise ValueError('actual single fresh start required')
    expected = {k: actual['guest'][k] for k in ['MainPID', 'InvocationID', 'Job', 'ExecMainStartTimestampMonotonic']}
    raw = 'SOURCE=' + repr(SOURCE) + '\nDIGEST=' + repr(BOM) + '\nEXPECTED=' + repr(expected) + '\n' + body()
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    (out / 'payload.private.py').write_text(raw)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=30)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'startedUTC': start, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'startsStops0': True, 'formalAccepted': False}
    if not r.returncode:
        value.update(json.loads(r.stdout))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
