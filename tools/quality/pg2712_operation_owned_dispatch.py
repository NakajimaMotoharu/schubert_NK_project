"""Single new-source owned stop after terminal/whole/parent18; no old replay."""
import inspect
import pg2556_strict_current_owned_dispatch as previous
from pg2708_operation_owned_sources import sources,context,SOURCE,TOOLS,bind
from pg2674_operation_publication_sources import candidate_bom
from pg2704_operation_current_full_seal import payload

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2712-operation-owned-stage-v1'
ARCHIVE='pg2712-'+TOOLS+'.tar'
POST_SLOT='pg2704-operation-current-full-seal-v1'


def namespace():
    ns={**previous.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'POST_SLOT':POST_SLOT,
      'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'candidate_bom':candidate_bom,'payload':payload}
    for fn in [previous.stage,previous.post_payload,previous.run_source,previous.run_action,previous.main]:
        exec(compile(bind(inspect.getsource(fn)),'<new source owned dispatch namespace>','exec'),ns)
    return ns


def stage():return namespace()['stage']()


def run_source():return namespace()['run_source']()


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
