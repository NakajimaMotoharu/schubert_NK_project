"""One ordinary53 reproduction on qualified API86 Main; no intermediate full replay."""
import json
import subprocess
import pg6316_outbox_graph_red as previous
from pg5940_private_lock_compile import BASE,W,sha

ROOT=previous.ROOT
OLD='65facffca6123ab4314864b4e934b6d4b007404e'
TESTS={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatcherTest.java'}
TESTS|={'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/'+n+'.java'
    for n in ('WebLogDispatcherTest','WebLogReplayWorkerTest')}


def prerequisites():
    p=BASE/'PG6320-outbox-graph-qualification-v1/manifest.json'
    if sha(p)!='55f826b2f0a116f198e3709f596f4e2a5a5be57e7364c0aabaea8ac60fcf3325':raise ValueError('exact original86 qualification')
    q=json.loads(p.read_bytes());private=W/'pg6320-outbox-graph-qualification-v1/manifest.safe.json'
    if sha(private)!=q['privateManifestSha256']:raise ValueError('original all Main/class proof')
    proof=json.loads(private.read_bytes())
    if(q['actualExit'],q['source'],q['tests'],q['suites'],q['sourceFiles'],q['physicalMain'])!=(0,OLD,86,15,851,1667):raise ValueError('genuine API86 only, not whole or other source')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 Main fixed before Web red')


def inventory():
    engine=previous.previous.prior.engine
    cases={module:set(values)for module,values in engine.CASES.items()}
    cases['api'].add('api.messaging.outbound.OutboxDispatcherTest')
    cases['web'].update(('web.logging.WebLogDispatcherTest','web.logging.WebLogReplayWorkerTest'))
    counts={engine.PACKAGE+name:len(previous.previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(53,10):raise ValueError('actual53 declarations/10 suites; no matrix inflation')
    return cases,counts


def runner():
    raw=previous.runner()
    for before,after in (('runner_source(38,9,target_count=16)','runner_source(53,10,target_count=17)'),
        ('pg6316-outbox-graph-red-v1','pg6322-web-graph-red-v1'),
        ("scope['targets']['api'].extend(('api/messaging/outbound/OwnedOutboxDispatcher','api/messaging/outbound/OutboxDispatcher'))",
         "scope['targets']['api'].append('api/messaging/outbound/OutboxDispatcher')\n    scope['targets']['web'].extend(('web/logging/WebLogDispatcher','web/logging/WebLogReplayWorker'))")):
        if raw.count(before)!=1:raise ValueError('one explicit53 current binding '+before)
        raw=raw.replace(before,after,1)
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed Test-only/operator first')
    prerequisites()
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=TESTS:
        raise ValueError('only three Test edits; every Main unchanged')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    scope={**vars(previous.previous.prior),'inventory':inventory}
    exec(compile(runner(),'<ordinary53 Web provider graph reproduction>','exec'),scope)
    return scope['run_red']()


if __name__=='__main__':raise SystemExit(main())
