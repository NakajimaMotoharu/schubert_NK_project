"""Explicit one stage/place only, never activation; all18/post qualification first."""
import json
import sys
import types
import pg5442_ownership_unused_dispatch as previous
import pg5608_current_unused_sources as role
import pg5610_current_unused_compile as compiler
import pg5614_current_unused_post as post
from pg4996_resume_connection import authenticate_host
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
TEMPLATE=previous.TEMPLATE


def stage_source():return role.normalized_text(previous.stage_source())


def source():return role.normalized_text(previous.source())


def before_record():
    role.qualify();fresh=json.loads(role.VIEW_LOCAL.read_bytes());v=fresh['result'];_,normal,_=role.current_tuple()
    # Every mapped predicate is derived from the new fresh full11 result, never
    # from the old stop completion or the earlier ten MainPID-only read.
    resources=v['allClientAdvisoryFlock0']and v['allKernelActor0']and v['allTenRefsReturnedNormally']
    if not resources or v['privateBeforeSha256']!=role.BEFORE or v['nativePhysicalFiles']!=94:raise ValueError('fresh all resources/full94 before required')
    return{**v,'genuineCompletion':normal,'currentOriginalClosedAndNoIntent':True,
      'runtimeConfigFilesToRetire':0,'runtimeAlreadyRetired':True,
      'allClientAdvisoryFlock0':v['allClientAdvisoryFlock0'],'allTenUnitsKernelEmpty':v['allKernelActor0'],
      'allResources0':resources,'snapshotOrigin':role.capture.SLOT,'snapshotSha256':role.BEFORE,'newDatabaseReads':0}


def runtime_namespace(candidate,before):
    return types.FunctionType(TEMPLATE.runtime_namespace.__code__,{**vars(TEMPLATE),'role':role,'TARGET':TARGET,'GUEST':GUEST,
      'stage_source':stage_source,'__file__':__file__})(candidate,before)


def main():
    if sys.argv[1:]not in(['stage'],['place']):raise ValueError('one explicit new-only action, no replay fallback')
    post.payload();authenticate_host();role.qualify()
    candidate=json.loads((role.W/'pg5598-candidate-build-v1.safe.json').read_bytes())
    scope=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate'in raw:raise ValueError('exactly one management critical gate')
    exec(compile(raw,'<unused current296/candidate0ea action only>','exec'),scope)
    with management_gate(P/'current-management-critical.lock'):return scope['main']()


if __name__=='__main__':raise SystemExit(main())
