"""Exactly one stage/place request with fresh host ownership and one management gate."""
import json
import sys
import types
import pg4710_ssc299_unused_dispatch as previous
import pg4864_ssc301_302_unused_sources as role
import pg4866_ssc301_302_unused_compile as compiler
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS


def stage_source():return role.normalized_text(previous.stage_source())


def source():return role.normalized_text(previous.source())


def before_record():
    role.qualify();value=json.loads(role.VIEW_LOCAL.read_bytes())['result']
    _,normal,_=role.current_tuple()
    if value['genuineCompletion']!=normal:raise ValueError('same actual stopped original/current data')
    # These are schema aliases of the actual fresh whole-resource predicate,
    # whose immutable verifier checked every kernel/client/advisory/flock twice.
    return {**value,'runtimeAlreadyRetired':value['runtimeConfigFilesToRetire']==0,
            'allClientAdvisoryFlock0':value['allResources0'],
            'allTenUnitsKernelEmpty':value['allResources0']}


def runtime_namespace(candidate,before):
    return types.FunctionType(previous.old.runtime_namespace.__code__,
        {**vars(previous.old),'role':role,'TARGET':TARGET,'GUEST':GUEST,
         'stage_source':stage_source,'__file__':__file__})(candidate,before)


def main():
    if sys.argv[1:] not in (['stage'],['place']):raise ValueError('one explicit action; no replay/resume')
    authenticate_host();role.qualify()
    candidate=json.loads((role.W/'pg4860-candidate-build-v1.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate' in raw:raise ValueError('one critical gate, never nested')
    exec(compile(raw,'<current825e distinct04bb unused action>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
