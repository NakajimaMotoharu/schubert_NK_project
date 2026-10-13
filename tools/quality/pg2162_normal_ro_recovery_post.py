"""Separate whole original/candidate post after pre-Ref RO ownership recovery."""
import json
import types
import pg2150_normal_unused_independent_post as prior

SLOT='pg2162-normal-ro-recovery-post-v1'


def payload():
    raw=prior.payload().replace('pg2150-normal-unused-independent-post-v1',SLOT)
    marker="save=base/'"+SLOT+"'"
    extra="require(not pathlib.Path('/proc/680258').exists()and not pathlib.Path('/proc/680289').exists())\nrequire(not pathlib.Path('/var/lib/pgpt-s1-preservation/pg2155-normal-candidate-host-ro-v1/complete.private').exists())\n"
    return raw.replace(marker,extra+marker)


def main():
    old=json.loads((prior.W/'pg2160-normal-ro-pair-owned-handoff-v1/manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or old['queuedSameHostGateAcquired']is not True:raise ValueError('actual current no-bus pair recovery required')
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'payload':payload})
    return fn()


if __name__=='__main__':raise SystemExit(main())
