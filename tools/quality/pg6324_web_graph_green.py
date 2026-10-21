"""One ordinary89 API/Web graph green; no replay of the intermediate full source."""
import json
import subprocess
import xml.etree.ElementTree as ET
import pg6322_web_graph_red as red
from pg5940_private_lock_compile import W

ROOT=red.ROOT
OLD='fb06b82db9db04837050e48c48899019312b133a'
MAIN={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/'+n+'.java'
    for n in ('WebLogDispatcher','WebLogReplayWorker')}


def inventory():
    cases,_=red.inventory()
    cases['api'].update(('api.messaging.outbound.OutboxFailureOwnershipTest','api.messaging.outbound.OwnedOutboxDispatcherTest'))
    cases['web'].update(('web.messaging.ArtemisRequestSenderTest','web.logging.WebLogMessageSenderTest','web.messaging.JmsRequestReplyClientTest'))
    engine=red.previous.previous.prior.engine
    counts={engine.PACKAGE+name:len(red.previous.previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(89,15):raise ValueError('actual89 declarations/15, no prior PASS arithmetic')
    return cases,counts


def reproduced():
    run=W/'pg6322-web-graph-red-v1';f=json.loads((run/'manifest.safe.json').read_bytes())
    expected={('dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest','graph323001ProviderFatalEdgesStopWithoutOrdinaryFailedCycle'),
        ('dev.codex.schubert.nk.web.logging.WebLogDispatcherTest','graph323002ProviderFatalNeverMarksOrdinaryFailureAndNullEdgesStillRetry')}
    found=set();total=[0,0,0,0];suites=0
    for p in(run/'source').glob('src/*/target/surefire-reports/TEST-*.xml'):
        r=ET.parse(p).getroot();suites+=1
        total=[a+int(r.get(k,0))for a,k in zip(total,('tests','failures','errors','skipped'))]
        for c in r.findall('testcase'):
            if c.find('failure')is not None:found.add((r.get('name'),c.get('name')))
    if not(f['source']==OLD and f['actualExit']==f['mavenActualExit']==1 and f['sourceFixed']
        and f['tests']==total[0]and f['suites']==suites and total[1:]==[2,0,0]
        and found==expected=={tuple(r)for r in f['failedOrSkipped']}):raise ValueError('original exact two Web graph XML failures, no skipped/error as expected reproduction')


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed Main/Test/operator first')
    reproduced()
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('two Web Main only; all independent red Test/oracles fixed')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    raw=red.runner()
    for before,after in (('runner_source(53,10,target_count=17)','runner_source(89,15,target_count=17)'),
        ('pg6322-web-graph-red-v1','pg6324-web-graph-selected-v1'),('def run_red():','def run_green():')):
        if raw.count(before)!=1:raise ValueError('one explicit89 current binding '+before)
        raw=raw.replace(before,after,1)
    scope={**vars(red.previous.previous.prior),'inventory':inventory}
    exec(compile(raw,'<ordinary89 grouped API and Web graph>','exec'),scope)
    return scope['run_green']()


if __name__=='__main__':raise SystemExit(main())
