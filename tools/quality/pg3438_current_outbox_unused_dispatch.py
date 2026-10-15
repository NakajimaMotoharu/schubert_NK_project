"""Separate new-only fixed tool stage and owned unused placement; no publication/start."""
import hashlib
import json
import sys
import types

import pg2660_operation_unused_dispatch as old
import pg3434_current_outbox_candidate_sources as role
import pg3436_current_outbox_candidate_compile as compiler
from pg1446_current_cold_stage import W, P
from pg1674_critical_management_gate import management_gate

TARGET = compiler.TARGET
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS


def bind(raw):
    for before, after in [(role.old.TOOLS, role.TOOLS), (role.old.SAVE, role.SAVE),
                          (role.old.ARCHIVE, role.ARCHIVE), (role.old.REMOTE, role.REMOTE),
                          ('pg2660-fixed-stage-v1', 'pg3438-fixed-stage-v1')]:
        raw = raw.replace(before, after)
    raw = compiler.bind(raw).replace('pg2660', 'pg3438').replace('PG2660', 'PG3438')
    raw = raw.replace('0.1.0-PG2512', '0.1.0-PG2802')
    return raw


STAGE = bind(old.STAGE)


def source():
    raw = bind(old.source())
    if raw.count('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0') != 1:
        raise ValueError('exact complete source input boundary required')
    raw = raw.replace('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0', role.SOURCE)
    compile(raw, '<current a9/new4856 distinct new-only stage/place>', 'exec')
    return raw


def before_record():
    path = W / 'pg3430-current-a9-readonly-before-v1/manifest.safe.json'
    proof = json.loads(path.read_bytes())
    view = json.loads((W / 'pg3432-current-a9-before-view-v2/manifest.safe.json').read_bytes())
    if (view['freshEqualityWitnessManifestSha256'] != hashlib.sha256(path.read_bytes()).hexdigest()
            or proof['actualExit'] != 0 or proof['productionSource'] != role.CURRENT
            or view['productionSource'] != role.CURRENT or not view['dataOnlyNotRuntimeAuthority']):
        raise ValueError('same authenticated data-only view and actual current Root completion proof')
    return {**view, 'genuineCompletion': proof['genuineCompletion']}


def runtime_namespace(candidate, before):
    if before.get('runtimeAlreadyRetired') is not True or before.get('dataOnlyNotRuntimeAuthority') is not True:
        raise ValueError('already-retired current data, not recovery authority')
    engine = old.previous.engine
    fn = types.FunctionType(engine.runtime_namespace.__code__,
                            {**engine.__dict__, 'CURRENT': role.CURRENT, 'BEFORE': role.BEFORE,
                             'TARGET': TARGET, 'GUEST': GUEST, 'REMOTE': role.REMOTE,
                             'STAGE': STAGE, 'production': role.production, 'sources': role.sources})
    return {**fn(candidate, before), '__file__': __file__}


def main():
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('explicit distinct stage/place only')
    role.qualify()
    candidate = json.loads((W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
    namespace = runtime_namespace(candidate, before_record())
    exec(compile(source(), '<new unused current/candidate dispatcher>', 'exec'), namespace)
    with management_gate(P / 'current-management-critical.lock'):
        return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
