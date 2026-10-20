"""Finite consumer-state PT; immutable original red artifacts, no real runtime operation."""
import argparse
import inspect
import json
import xml.etree.ElementTree as ET
import pg5732_enum48_selected as engine

CASES={**engine.CASES,
 'api':{'api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest'},
 'web':{'web.messaging.ReplyRollbackUnconfirmedContractTest'}}
RED_API={('dev.codex.schubert.nk.api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest',m)for m in(
 'syncRollbackUnconfirmedStopsAllFourContexts','questionRollbackUnconfirmedStopsFurtherWork','webLogRollbackUnconfirmedStopsFurtherLogs')}
RED_WEB={('dev.codex.schubert.nk.web.messaging.ReplyRollbackUnconfirmedContractTest','rollbackUnconfirmedMakesReplyOwnerUnreadyAndStopsFurtherDecode')}


def red_qualified(snapshot,actual,expected,physical,exits,problems,phase):
    base=engine.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    qp=base/'PG5780-current3939-cases/qualification.json'
    if engine.sha(qp)!='1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45':raise ValueError('original3939 source anchor')
    q=json.loads(qp.read_bytes());sp=engine.ROOT.parent/'pgpt-runs/PG379/pg5776-jms-primary-static-v1/manifest.safe.json'
    proof=json.loads(sp.read_bytes())
    if engine.sha(sp)!=json.loads((base/'PG5776-jms-primary-static-v1/manifest.json').read_bytes())['privateManifestSha256']:raise ValueError('originalMain source hashes')
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    wanted=RED_API if phase=='red-api'else RED_WEB
    wanted_inventory={k:v for k,v in expected.items()if phase!='red-api'or'.web.'not in k}
    actual_physical={k:v for k,v in q['allPhysicalMainSha256'].items()if phase!='red-api'or not k.startswith('web:')}
    failures=[]
    for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        for case in ET.parse(p).getroot().findall('testcase'):
            if any(c.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for c in case.iter()):return False
            failures.extend(f.get('type')for f in case.findall('failure'))
    return sources==proof['allSourceHashes']and physical==actual_physical and actual==wanted_inventory and exits==[0,1]and {tuple(r)for r in problems}==wanted and len(failures)==len(wanted)and set(failures)=={'org.opentest4j.AssertionFailedError'}


def runner_source(phase):
    raw=inspect.getsource(engine.main)
    count=9 if phase=='red-web'else 11
    changes={
      "'-B','-o','-ntp'":"'-B','-o','-ntp','-fae'",
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'or module=='api'and PHASE=='red-api'else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!='+str(count),
      "'expectedTests':12":"'expectedTests':"+str(count),
      'len(target_counters)==14':'len(target_counters)==0',
      '    done=done and target100':'    # Full-class coverage remains a separate source-bound acceptance requirement.',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(phase=PHASE,executionKind='NORMAL_FINITE_ROLLBACK_STATE_PT',purposefulRedEstablished=red_qualified(snapshot,actual,expected,physical,exits,problems,PHASE),webNotRunRetained=PHASE=='red-api',noRuntimeOrVmOperation=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact finite runner predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite rollback-state fixture>','exec')
    return raw


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red-api','red-web'));phase=parser.parse_args().phase
    namespace={**vars(engine),'SLOT':'pg5794-rollback-'+phase+'-v1','CASES':{**CASES,'api':engine.CASES['api']}if phase=='red-web'else CASES,'TARGETS':{},'PHASE':phase,'red_qualified':red_qualified}
    exec(compile(runner_source(phase),'<finite rollback-state fixture>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
