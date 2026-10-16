"""Separate one-time tool stage and owned unused placement only; no current publication/start."""
import hashlib
import json
import sys
import types
import pg3438_current_outbox_unused_dispatch as previous
import pg3756_hygiene_unused_sources as role
import pg3758_hygiene_unused_compile as compiler
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

TARGET=compiler.TARGET;GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS


def bind(raw):
    return role.role_text(raw)


STAGE=bind(previous.STAGE).replace('PG3760_IMMUTABLE_STAGE_V2','PG3760_IMMUTABLE_STAGE_V1')


def source():
    raw=bind(previous.source()).replace('pg3760-stage-v2.exit','pg3760-stage-v1.exit')
    marker="current=json.loads((W/'pg3754-current-4856-before-view-v1/manifest.safe.json').read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one explicit host current receipt consumer')
    raw=raw.replace(marker,"current=json.loads((W/"+repr(str(role.VIEW_LOCAL.relative_to(W)))+").read_bytes())['result']")
    compile(raw,'<new source-bound immutable stage and unused placement>','exec');return raw


def before_record():
    path=W/'pg3752-current-preservation-readonly-v1/manifest.safe.json';raw=path.read_bytes();proof=json.loads(raw);view=json.loads(role.VIEW_LOCAL.read_bytes());r=proof['result'];v=view['result'];_,normal,_=role.current_tuple()
    if not(proof['actualExit']==view['actualExit']==0 and view['freshReadOnlyProofSha256']==hashlib.sha256(raw).hexdigest()and r['deployedSource']==v['productionSource']==role.CURRENT and r['BOM']==role.CURRENT_BOM and v['privateBeforeSha256']==role.BEFORE and v['dataOnlyNotRuntimeAuthority']and r['currentOriginalClosedAndNoIntent']and r['runtimeStartupNativeExactMetadataAndSha']):raise ValueError('exact current authenticated data and retired runtime, never old authority')
    return {**v,'genuineCompletion':normal,'runtimeAlreadyRetired':True,'allClientAdvisoryFlock0':r['dbClientsAdvisoryMA0'],'allTenUnitsKernelEmpty':r['allTenKernelJob0']}


def runtime_namespace(candidate,before):
    if before.get('runtimeAlreadyRetired')is not True or before.get('dataOnlyNotRuntimeAuthority')is not True:raise ValueError('retired current data only')
    engine=previous.old.previous.engine;fn=types.FunctionType(engine.runtime_namespace.__code__,{**engine.__dict__,'CURRENT':role.CURRENT,'BEFORE':role.BEFORE,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':role.REMOTE,'STAGE':STAGE,'production':role.production,'sources':role.sources});return {**fn(candidate,before),'__file__':__file__}


def main():
    role.qualify();candidate=json.loads((W/'pg3748-candidate-build-v1.safe.json').read_bytes());ns=runtime_namespace(candidate,before_record());raw=source()
    if 'management_gate'in raw:raise ValueError('do not nest management gates')
    exec(compile(raw,'<new unused operator, explicit action required>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':
    if sys.argv[1:]not in [['stage'],['place']]:raise SystemExit('one explicit stage/place action required; no replay/resume alias')
    raise SystemExit(main())
