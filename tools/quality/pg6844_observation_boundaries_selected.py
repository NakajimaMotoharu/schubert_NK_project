"""Two new data-only Test classes with unchanged related suites and six finite module guards."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT,W,BASE

OLD='4c0343a55b5fe41dad766a520558363e81f01541'
TESTS={
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/AcceptorObjectBoundaryTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/PostgresObservationRowsTest.java'}
SLOT='pg6844-observation-boundaries-selected-v1'
EXPECTED=(23,11)


def inventory():
    return profile.inventory({'batch':{'batch.mq.AcceptorObjectBoundaryTest','batch.mq.ArtemisAcceptorReadinessClientTest',
      'batch.file.PostgresObservationRowsTest','batch.file.MorningGateEvidenceTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=TESTS:raise ValueError('only two new literal-data Test classes; all Main/old tests fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('all quality/build/Current inputs fixed')


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source);cases,_=inventory()
    return prior.qualification_definition()(source,run,cases,EXPECTED,set(),
      BASE/'PG6826-api-management-result-original-v1/manifest.json','8098c42d9af5490123b9a60fcfcb7a79c8f9f432862a34864078a4cb11e16f59',
      W/'pg6826-api-management-result-original-v1/manifest.safe.json',W/'pg6826-api-management-result-original-v1/findings.safe.json',
      'pg6846-observation-boundaries-original-v1','PG6846-observation-boundaries-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'))
    if p.parse_args().action=='read':return read_original()
    cases,counts=inventory();scope={**vars(profile),'runner':prior.runner}
    exec(compile(inspect.getsource(profile.execute),'<finite observation data boundaries>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'batch':['batch/mq/ArtemisAcceptorReadinessClient']})


if __name__=='__main__':main()
