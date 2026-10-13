"""Immutable new-only question candidate stage/place, no Root/Backup/reload/start."""
import json
import sys
import types
import pg2134_current_normal_unused_dispatch as prior
from pg2412_question_unused_sources import sources,bind,TOOLS,BEFORE,CURRENT,REMOTE,production
from pg2413_question_unused_compile import TARGET
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
STAGE = bind(prior.STAGE).replace('pg2134-fixed-stage-v1','pg2414-fixed-stage-v1')


def source():
    raw = bind(prior.source()).replace('pg2134-','pg2414-').replace('pg2133-frozen','pg2413-frozen')
    compile(raw,'<actual immutable new question stage/place>','exec')
    return raw


def runtime_namespace(candidate,before):
    function = types.FunctionType(prior.runtime_namespace.__code__,
        {**prior.__dict__,'CURRENT':CURRENT,'BEFORE':BEFORE,'TARGET':TARGET,'GUEST':GUEST,
         'REMOTE':REMOTE,'STAGE':STAGE,'production':production,'sources':sources})
    if before.get('runtimeAlreadyRetired') is not True:
        raise ValueError('actual completed retired current required')
    return {**function(candidate,before),'__file__':__file__}


def main():
    if sys.argv[1:] not in (['stage'],['place']):
        raise ValueError('immutable stage/place only')
    candidate = json.loads((W/'pg2406-candidate-build-v1.safe.json').read_bytes())
    before = json.loads((W/'pg2410-retired-current-before-v1/manifest.safe.json').read_bytes())
    namespace = runtime_namespace(candidate,before)
    exec(compile(source(),'<direct fixed question new/current entry>','exec'),namespace)
    with management_gate(P/'current-management-critical.lock'):
        return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
