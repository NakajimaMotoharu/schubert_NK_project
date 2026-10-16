"""One explicit unused stage/place action with current ownership authentication."""
import inspect
import json
import sys
import types
import pg3986_literal_invariant_unused_dispatch as old
import pg4706_ssc299_unused_sources as role
import pg4708_ssc299_unused_compile as compiler
from pg4434_current_candidate_admission_read import authenticate_host

TARGET = compiler.TARGET
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS


def stage_source(): return role.normalized_text(old.stage_source())


def source(): return role.normalized_text(old.source())


def before_record():
    role.qualify(); v = json.loads(role.VIEW_LOCAL.read_bytes())['result']
    _, normal, _ = role.current_tuple()
    if v['genuineCompletion'] != normal:
        raise ValueError('fresh data and same completed normal original required')
    # State predicate only: no old resume file exists; no retirement command was issued.
    return {**v, 'runtimeAlreadyRetired': v['runtimeConfigFilesToRetire'] == 0}


def runtime_namespace(candidate,before):
    return types.FunctionType(old.runtime_namespace.__code__,
        {**vars(old),'role':role,'TARGET':TARGET,'GUEST':GUEST,
         'stage_source':stage_source,'__file__':__file__})(candidate,before)


def main():
    if sys.argv[1:] not in [['stage'], ['place']]:
        raise ValueError('exact one stage/place action, no replay/resume alias')
    authenticate_host()
    ns={**vars(old),'role':role,'compiler':compiler,'TARGET':TARGET,'GUEST':GUEST,
        'before_record':before_record,'runtime_namespace':runtime_namespace,
        'source':source,'__file__':__file__}
    exec(compile(inspect.getsource(old.main),'<normal current unused explicit action>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
