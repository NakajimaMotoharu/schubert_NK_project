"""One stage/place action, same current metadata predicates and one management gate."""
import json
import sys
import types
import pg4868_ssc301_302_unused_dispatch as previous
import pg4986_ssc304_unused_sources as role
import pg4988_ssc304_unused_compile as compiler
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
TEMPLATE=previous.previous.old


def stage_source():return role.normalized_text(previous.stage_source())


def source():return role.normalized_text(previous.source())


def before_record():
    role.qualify();value=json.loads(role.VIEW_LOCAL.read_bytes())['result'];_,normal,_=role.current_tuple()
    past=json.loads((role.W/'pg4922-current-owned-post-v1/manifest.safe.json').read_bytes())
    record=past.get('result',past)
    if type(past['actualExit'])is not int or past['actualExit']!=0 or record['productionSource']!=role.CURRENT or record['genuineCompletion']!=normal:
        raise ValueError('same actual closed current Root proof as immutable history only')
    # Same aliases as approved4862/4868: exact executed payload hash includes
    # absent active + start.intent, full runtime/originals preservation and all
    # ten kernel/client/advisory/flock predicates. Not a new OS/start permission.
    return {**value,'genuineCompletion':normal,'currentOriginalClosedAndNoIntent':True,
        'runtimeConfigFilesToRetire':0,'runtimeAlreadyRetired':True,
        'allClientAdvisoryFlock0':value['allResources0'],'allTenUnitsKernelEmpty':value['allResources0']}


def runtime_namespace(candidate,before):
    return types.FunctionType(TEMPLATE.runtime_namespace.__code__,{**vars(TEMPLATE),'role':role,
        'TARGET':TARGET,'GUEST':GUEST,'stage_source':stage_source,'__file__':__file__})(candidate,before)


def main():
    if sys.argv[1:]not in(['stage'],['place']):raise ValueError('one explicit action, no replay/resume')
    authenticate_host();role.qualify()
    candidate=json.loads((role.W/'pg4980-candidate-build-v1.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate'in raw:raise ValueError('one critical gate, never nested')
    exec(compile(raw,'<current04bb distinct SSC304 unused action>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
