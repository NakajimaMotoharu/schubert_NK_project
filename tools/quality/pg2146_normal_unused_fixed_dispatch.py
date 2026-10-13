"""New-only immutable normal unused stage/place after BUG1213 full recovery."""
import json
import types
import pg2134_current_normal_unused_dispatch as prior
from pg2144_normal_unused_fixed_sources import bind,sources,TOOLS,REMOTE
from pg2145_normal_unused_fixed_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE)


def source():return bind(prior.source()).replace('pg2133-frozen','pg2145-frozen')


def runtime_namespace(candidate,before):
    ns=prior.runtime_namespace(candidate,before)
    return {**ns,'__file__':__file__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources}


def main():
    post=json.loads((prior.W/'pg2142-current-normal-pair-recovery-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['candidateNotPlaced']is not True or post['guest']['ownedActorsDBAdvisoryFlockGone']is not True:
        raise ValueError('actual full current recovery required')
    ns={**prior.__dict__,'__file__':__file__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'source':source,'runtime_namespace':runtime_namespace}
    fn=types.FunctionType(prior.main.__code__,ns)
    return fn()


if __name__=='__main__':raise SystemExit(main())
