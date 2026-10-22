"""Combined own Web lifecycle and pure public correlation data tests; no actual recovery."""
import argparse
import ast
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6054_expiry_read_qualification as original
import pg6780_web_management_result_selected as previous
from pg5940_private_lock_compile import ROOT,W,BASE

OLD='3c5f03d4aca569e4f5e722d7357e04749ad0998c'
MAIN=previous.MAIN
TESTS={
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchBoundaryTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryRequestBoundaryTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/FailedProfileBoundaryTest.java'}
SLOT='pg6798-web-correlation-selected-v1'
EXPECTED=(48,16)
MEASURED_TARGETS={'web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class',
 'batch:dev/codex/schubert/nk/batch/file/StartupLaunchRecord.class',
 'batch:dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry.class',
 'batch:dev/codex/schubert/nk/batch/platform/CleanupFailedBackupRequest.class'}


def inventory():
    if EXPECTED is None:raise ValueError('freeze original source declaration inventory before any run')
    return profile.inventory({'web':{'web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest','web.bootstrap.WebRuntimeStopTest'},
      'batch':{'batch.file.StartupLaunchBoundaryTest','batch.file.StartupLaunchRecordTest','batch.platform.ExpiryRequestBoundaryTest','batch.platform.ExpiryWorkerRequestTest','batch.platform.FailedProfileBoundaryTest','batch.platform.CleanupFailedBackupRequestTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={MAIN}|TESTS:raise ValueError('one necessary Web Main and exactly three new Test files, every prior oracle fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('quality/build/Current fixed')
    from pg6796_web_early_cleanup_proof import verify_source
    verify_source()


def qualification_definition():
    raw=inspect.getsource(original.qualify)
    before="targetCounters={k: v for k, v in counters.items() if any(k == o+'.class' or k.startswith(o+'$') for o in owners)}"
    if raw.count(before)!=1:raise ValueError('one measured target selection, physical changed-owner guard not altered')
    raw=raw.replace(before,'targetCounters={k:v for k,v in counters.items() if k in MEASURED_TARGETS}',1)
    tree=ast.parse(raw)
    if sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==1667 for x in ast.walk(tree))!=3:raise ValueError('three exact current1669 dimensions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant(1669),node)if type(node.value)is int and node.value==1667 else node
    scope={**vars(original),'MEASURED_TARGETS':MEASURED_TARGETS}
    exec(compile(ast.fix_missing_locations(Counts().visit(tree)),'<current1669 measured Web and pure correlation>','exec'),scope);return scope['qualify']


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source);cases,_=inventory()
    return qualification_definition()(source,run,cases,EXPECTED,{MAIN},
      BASE/'PG6782-web-management-result-original-v1/manifest.json','60eb1d48db665286a8cfd5d4495c51b80e1ee6cce7af282595a96f5f07f99539',
      W/'pg6782-web-management-result-original-v1/manifest.safe.json',W/'pg6782-web-management-result-original-v1/findings.safe.json',
      'pg6800-web-correlation-original-v1','PG6800-web-correlation-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'));action=p.parse_args().action
    if action=='read':return read_original()
    cases,counts=inventory();scope={**vars(profile),'runner':previous.runner}
    exec(compile(inspect.getsource(profile.execute),'<combined normal current1669>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'web':['web/bootstrap/WebManagementServer'],
      'batch':['batch/file/StartupLaunchRecord','batch/platform/CleanupWorkerRequest$Expiry','batch/platform/CleanupFailedBackupRequest']})


if __name__=='__main__':main()
