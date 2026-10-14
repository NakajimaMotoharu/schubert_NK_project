"""Separate full post after owned Ref/Java handoff, no old-close normalization."""
import types
import pg2940_current_resume_before as previous
from pg1446_current_cold_stage import W
import json

SLOT = 'pg2968-recovered-pair-full-post-v1'


def payload(seals):
    raw = previous.payload(seals).replace(previous.SLOT, SLOT).replace('PG2940-current-resume-before-v1', 'PG2968-recovered-pair-full-post-v1')
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one independent full post scope required')
    checks = """
recovered=base/'pg2966-retained-pair-owned-handoff-v1'
require((recovered/'complete.private').read_bytes()==b'ownedRefThenJavaGone=true\\nallOldResources0=true\\noldCloseUnknown=true\\nfullIndependentPostPending=true\\n')
require(not any(pathlib.Path('/proc',str(pid)).exists()for pid in[118988,119019]))
failed=base/'pg2954-current-cold-resume-preparation-v1'
require({p.name for p in failed.iterdir()}=={'refs-prepare.private.log'})
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='f176d954ada998d12fec8a7227f66882d208aebce430f107823c36eeb123910e')
"""
    return raw.replace(marker, '\n' + checks + marker)


def entry():
    receipt = json.loads((W / 'pg2966-retained-pair-owned-handoff-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or not receipt['gateHandoffComplete'] or not receipt['oldCloseUnknown']:
        raise ValueError('qualified owned recovery required')
    fn = previous.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'recovered_pair_full_post')


if __name__ == '__main__':
    raise SystemExit(entry()())
