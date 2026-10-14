"""New-only stage/place in authenticated scopes; no publication or business replay."""
import json
import sys
import types
import pg2434_current_boot_question_dispatch as previous
import pg2134_current_normal_unused_dispatch as engine
from pg2516_current_strict_candidate_sources import sources, bind, TOOLS, BEFORE, CURRENT, REMOTE, production
from pg2517_current_strict_candidate_compile import TARGET
from pg1446_current_cold_stage import W, P
from pg1674_critical_management_gate import management_gate

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
STAGE = bind(previous.STAGE)


def source():
    raw = bind(previous.source()).replace('pg2433-frozen', 'pg2517-frozen')
    compile(raw, '<new fixed candidate stage/place body>', 'exec')
    return raw


def runtime_namespace(candidate, before):
    if before.get('runtimeAlreadyRetired') is not True:
        raise ValueError('actual already-retired current required; no retirement replay')
    fn = types.FunctionType(engine.runtime_namespace.__code__,
        {**engine.__dict__, 'CURRENT': CURRENT, 'BEFORE': BEFORE, 'TARGET': TARGET,
         'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': STAGE, 'production': production, 'sources': sources})
    return {**fn(candidate, before), '__file__': __file__}


def main():
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('distinct new-only stage/place only')
    candidate = json.loads((W / 'pg2512-candidate-build-v1.safe.json').read_bytes())
    before = json.loads((W / 'pg2514-current-cdbc-before-v2/manifest.safe.json').read_bytes())
    ns = runtime_namespace(candidate, before)
    exec(compile(source(), '<new unused candidate direct entry>', 'exec'), ns)
    with management_gate(P / 'current-management-critical.lock'):
        return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
