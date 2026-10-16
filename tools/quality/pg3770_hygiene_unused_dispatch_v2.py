"""New-only v2 stage/place reservations; original failed v1 remains immutable."""
import json
import sys
import types
import pg3760_hygiene_unused_dispatch as previous
import pg3766_hygiene_unused_sources_v2 as role
import pg3768_hygiene_unused_compile_v2 as compiler
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET;GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
STAGE=role.bind(previous.STAGE)
before_record=previous.before_record


def source():
    raw=role.bind(previous.source());compile(raw,'<v2 new reservations only>','exec');return raw


def runtime_namespace(candidate,before):
    if before.get('runtimeAlreadyRetired')is not True or before.get('dataOnlyNotRuntimeAuthority')is not True:raise ValueError('authenticated current data only')
    engine=previous.previous.old.previous.engine;fn=types.FunctionType(engine.runtime_namespace.__code__,{**engine.__dict__,'CURRENT':role.CURRENT,'BEFORE':role.BEFORE,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':role.REMOTE,'STAGE':STAGE,'production':role.production,'sources':role.sources});return {**fn(candidate,before),'__file__':__file__}


def main():
    role.qualify();candidate=json.loads((W/'pg3748-candidate-build-v1.safe.json').read_bytes());ns=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate'in raw:raise ValueError('do not nest management gate')
    exec(compile(raw,'<new v2 actual operator>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':
    if sys.argv[1:]not in [['stage'],['place']]:raise SystemExit('one explicit new-only action required')
    raise SystemExit(main())
