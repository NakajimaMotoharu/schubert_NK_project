"""Single authenticated a9 owned stop, all genuine current dependencies explicit."""
import inspect
import pg2712_operation_owned_dispatch as prior
from pg2890_network_owned_sources import sources,context,SOURCE,TOOLS,bind
from pg2862_network_newcurrent_observer import BOM
from pg2902_network_after_chr_full_seal import payload as seal_payload

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2894-network-owned-stage-v1'
ARCHIVE='pg2894-'+TOOLS+'.tar'
POST_SLOT='pg2902-network-after-chr-full-seal-v1'


def namespace():
    ns={**prior.previous.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'POST_SLOT':POST_SLOT,
        'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'candidate_bom':lambda:BOM,'payload':seal_payload}
    for fn in [prior.previous.stage,prior.previous.post_payload,prior.previous.run_source,prior.previous.run_action,prior.previous.main]:
        exec(compile(bind(inspect.getsource(fn)),'<closed actual a9 once owned dispatch>','exec'),ns)
    return ns


def stage():return namespace()['stage']()
def run_source():return namespace()['run_source']()
def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
