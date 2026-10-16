"""BUG1350 exact read-only difference after pre-signal refusal; no recovery replay."""
import hashlib
import json
import os
import subprocess
import pg4336_current_unknown_read as previous
from pg4060_original_profile_dual_stack import once
from pg1446_current_cold_stage import W, SSH
from pg4152_exact_failed_done_recover import durable, process

SLOT = 'pg4354-current-reference-delta-v1'


def payload():
    raw = once(previous.payload(), "save=base/'" + previous.SLOT + "'", "save=base/'" + SLOT + "'")
    # Historical emitted unused imports are removed, not suppressed.
    raw = once(raw, 'import json,hashlib,os,subprocess,datetime', 'import json,hashlib,os,subprocess')
    raw = once(raw, 'import base64,selectors', 'import base64')
    marker = "sha_private=save_private('observed.private.json',private)"
    insert = """refraw=(base/'pg4336-current-unknown-read-v1/observed.private.json').read_bytes();require(hashlib.sha256(refraw).hexdigest()=='92bb9a17f47de3c2bcbee713e5e5e28cb7336702c0f2d4a5d9495fec3b9dcc5f')
reference=json.loads(refraw)['samples'][-1]
reference_delta={key:differences(reference[key],samples[-1][key])for key in fixedkeys if reference[key]!=samples[-1][key]}
private['referenceDelta']=reference_delta
private['reference']=reference
"""
    raw = once(raw, marker, insert + marker)
    return once(raw, "'originalFailedPairAvailable':False", "'referenceDeltaPaths':reference_delta,'originalFailedPairAvailable':False")


def main():
    start = json.loads((previous.ORIGINAL / 'start.safe.json').read_bytes())
    ssh = json.loads((previous.ORIGINAL / 'ssh.private.json').read_bytes())
    if process(start['owner']['pid']) != start['owner'] or process(ssh['pid']) != ssh:
        raise ValueError('same original retained host required')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload()
    compile(raw, '<current reference delta>', 'exec')
    with (out / 'payload.private.py').open('x') as f:
        f.write(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-', 'inspect'],
                       input=raw.encode(), capture_output=True, timeout=180)
    for name, content in [('stdout.private.log', r.stdout), ('stderr.private.log', r.stderr)]:
        with (out / name).open('xb') as f:
            f.write(content)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'operationsIssued': 0}
    if r.returncode == 0:
        value['result'] = json.loads(r.stdout)
    durable(out / 'manifest.safe.json', value)
    print(json.dumps(value))


if __name__ == '__main__':
    main()
