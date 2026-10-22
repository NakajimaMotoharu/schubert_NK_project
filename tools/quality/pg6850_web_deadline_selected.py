"""Original ordinary Web stop-deadline counterexample and identical-oracle green component."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT,W,BASE,sha

OLD='b2514bf6d80c873ab23940ebae293b95686c1c57'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebManagementDeadlineTest.java'
RED='pg6856-web-deadline-red-v3'
GREEN='pg6852-web-deadline-green-v1'
EXPECTED=(42,15)


def inventory(red=False):
    if red:return profile.inventory({'web':{'web.bootstrap.WebManagementDeadlineTest'}},(15,8))
    return profile.inventory({'batch':{'batch.mq.AcceptorObjectBoundaryTest','batch.mq.ArtemisAcceptorReadinessClientTest','batch.file.PostgresObservationRowsTest','batch.file.MorningGateEvidenceTest'},
      'web':{'web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest','web.bootstrap.WebRuntimeStopTest','web.bootstrap.WebManagementDeadlineTest'}},EXPECTED)


def guard(source,green):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=({MAIN,TEST}if green else{TEST}):raise ValueError('exact one new Test and only green Web Main; all old oracles fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('all build/quality/Current inputs fixed')


def red_guard(source):return guard(source,False)
def green_guard(source):
    guard(source,True)
    path=BASE/'PG6858-web-deadline-red-original-v1/manifest.json'
    if sha(path)!='9a9c504cd8712ea90672f29ec603b788ddc897eb887b66194f7a6d10519232f1':raise ValueError('frozen genuine three counterexamples first')
    red=json.loads(path.read_bytes())
    if not(red['readerActualExit']==0 and red['originalActualExit']==1 and red['productionCounterexamplesReproduced']==3
      and sha(ROOT/TEST)==red['testSourceSha256']):raise ValueError('same actual red Test bytes for green')
    if subprocess.check_output(['git','diff',red['source'],source,'--',':(glob)src/*/src/test/**/*'],cwd=ROOT):raise ValueError('all old and new Test/oracle bytes fixed since red')


def read_green():
    run=W/GREEN;source=json.loads((run/'begin.safe.json').read_bytes())['source'];green_guard(source);cases,_=inventory()
    return prior.qualification_definition()(source,run,cases,EXPECTED,{MAIN},
      BASE/'PG6846-observation-boundaries-original-v1/manifest.json','28748350e9f1d67cfb0e1addb43b073b398eee3f105d7948e1bf70c3e6dbd458',
      W/'pg6846-observation-boundaries-original-v1/manifest.safe.json',W/'pg6846-observation-boundaries-original-v1/findings.safe.json',
      'pg6854-web-deadline-original-v1','PG6854-web-deadline-original-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('red','green','read-green'));action=parser.parse_args().action
    if action=='read-green':return read_green()
    cases,counts=inventory(action=='red');scope={**vars(profile),'runner':prior.runner}
    exec(compile(inspect.getsource(profile.execute),'<finite ordinary Web stop deadline>','exec'),scope)
    expected=(15,8)if action=='red'else EXPECTED
    return scope['execute'](GREEN if action=='green'else RED,green_guard if action=='green'else red_guard,cases,counts,expected,{'web':['web/bootstrap/WebManagementServer']})


if __name__=='__main__':main()
