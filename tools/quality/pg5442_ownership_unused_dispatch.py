"""One explicit stage/place, exact fresh before/native88/296 ABI; never current publication."""
import json
import sys
import types
import pg4990_ssc304_unused_dispatch as previous
import pg5438_ownership_unused_sources as role
import pg5440_ownership_unused_compile as compiler
import pg5444_ownership_unused_post as post
from pg4996_resume_connection import authenticate_host
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
TEMPLATE=previous.TEMPLATE


def stage_source():return role.normalized_text(previous.stage_source())


def source():return role.normalized_text(previous.source())


def before_record():
    role.qualify();v=json.loads(role.VIEW_LOCAL.read_bytes())['result']
    full=json.loads((role.W/role.view.before.SLOT/'manifest.safe.json').read_bytes())
    result=full['result'];_,normal,_=role.current_tuple()
    if type(full['actualExit'])is not int or full['actualExit']!=0 or full['source']!=role.CURRENT or (
        result['productionSource']!=role.CURRENT or result['beforeSha256']!=v['snapshotSha256']or
        result['allResources0']is not True or result['normalNewReferences']is not True or result['nativePhysicalFiles']!=88):
        raise ValueError('exact5434 real client/advisory/flock/kernel/original preservation, not invented aliases')
    return {**v,'genuineCompletion':normal,'runtimeAlreadyRetired':True,
        'allClientAdvisoryFlock0':result['allResources0'],'allTenUnitsKernelEmpty':result['allResources0']}


def runtime_namespace(candidate,before):
    return types.FunctionType(TEMPLATE.runtime_namespace.__code__,{**vars(TEMPLATE),'role':role,
        'TARGET':TARGET,'GUEST':GUEST,'stage_source':stage_source,'__file__':__file__})(candidate,before)


def main():
    if sys.argv[1:]not in(['stage'],['place']):raise ValueError('one explicit new-only action, no auto replay')
    # Preserve the already-built independent post as an admission prerequisite.
    post.payload();authenticate_host();role.qualify()
    candidate=json.loads((role.W/'pg5430-candidate-build-v1.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate'in raw:raise ValueError('exactly one management critical gate')
    exec(compile(raw,'<currentA2/candidate296 unused action only>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
