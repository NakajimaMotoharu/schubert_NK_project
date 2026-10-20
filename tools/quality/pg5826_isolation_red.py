"""Eight independent isolation policy reds; all original3955 Main preserved, no runtime operation."""
import argparse
import inspect
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
import pg5732_enum48_selected as engine

CASES={**engine.CASES,'api':{'api.messaging.inbound.FatalIsolationConsumersContractTest'},'web':{'web.messaging.ReplyFatalIsolationContractTest'}}
RED_API={('dev.codex.schubert.nk.api.messaging.inbound.FatalIsolationConsumersContractTest',m)for m in(
 'iso001SyncCheckedIsolationFailureStopsWithoutAck','iso002SyncRuntimeIsolationFailureStopsWithoutAck',
 'iso003QuestionCheckedIsolationFailureStopsWithoutAck','iso004QuestionRuntimeIsolationFailureStopsWithoutAck',
 'iso005WebLogCheckedIsolationFailureStopsWithoutAck','iso006WebLogRuntimeIsolationFailureStopsWithoutAck')}
RED_WEB={('dev.codex.schubert.nk.web.messaging.ReplyFatalIsolationContractTest',m)for m in(
 'iso007ReplyCheckedIsolationFailureStopsWithoutAck','iso008ReplyRuntimeIsolationFailureStopsWithoutAck')}


def expected_assertions(message,web):
    pairs=Counter(re.findall(r'expected: <([^>]+)> but was: <([^>]+)>',message or''))
    wanted=Counter({('false','true'):1,('1','0'):1})
    if web:wanted[('true','false')]=1
    return pairs==wanted


def red_qualified(snapshot,actual,expected,physical,exits,problems,phase):
    base=engine.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';qp=base/'PG5808-current3955-cases/qualification.json'
    if engine.sha(qp)!='42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376':raise ValueError('original3955 physical reference')
    q=json.loads(qp.read_bytes());sp=engine.ROOT.parent/'pgpt-runs/PG379/pg5810-rollback-static-reauth-v1/manifest.safe.json';pub=base/'PG5810-rollback-static-reauth-v1/manifest.json'
    if engine.sha(pub)!='68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23'or engine.sha(sp)!=json.loads(pub.read_bytes())['privateManifestSha256']:raise ValueError('original850 Main source proof')
    proof=json.loads(sp.read_bytes());sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    wanted=RED_API if phase=='red-api'else RED_WEB;inventory={k:v for k,v in expected.items()if phase!='red-api'or'.web.'not in k};classes={k:v for k,v in q['allPhysicalMainSha256'].items()if phase!='red-api'or not k.startswith('web:')};failures=[]
    for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        for case in ET.parse(p).getroot().findall('testcase'):
            if any(n.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in case.iter()):return False
            for failure in case.findall('failure'):
                if failure.get('type')not in('org.opentest4j.AssertionFailedError','org.opentest4j.MultipleFailuresError')or not expected_assertions(failure.get('message'),phase=='red-web'):return False
                failures.append((case.get('classname'),case.get('name','').removesuffix('()')))
    return sources==proof['allSourceHashes']and physical==classes and actual==inventory and exits==[0,1]and {tuple(r)for r in problems}==wanted and set(failures)==wanted and len(failures)==len(wanted)


def runner_source(phase):
    raw=inspect.getsource(engine.main);count=15 if phase=='red-api'else 10
    replacements={
      "'-B','-o','-ntp'":"'-B','-o','-ntp','-fae'",
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'else 6 if module=='api'and PHASE=='red-api'else 2 if module=='web'else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!='+str(count),
      "'expectedTests':12":"'expectedTests':"+str(count),
      'len(physical)==1664':'len(physical)==1665',
      'len(target_counters)==14':'len(target_counters)==0',
      '    done=exits==[0,0]':'    target100=False # No target counters requested, never vacuous100.\n    done=exits==[0,0]',
      '    done=done and target100':'    # Purposeful red remains a failure, never a PASS or coverage success.',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(phase=PHASE,executionKind='NORMAL_ISOLATION_POLICY_RED',purposefulRedEstablished=red_qualified(snapshot,actual,expected,physical,exits,problems,PHASE),webNotRunRetained=PHASE=='red-api',noRuntimeOrVmOperation=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('one exact finite isolation red predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite independent eight isolation reds>','exec');return raw


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red-api','red-web'));phase=parser.parse_args().phase
    scope={**vars(engine),'SLOT':'pg5826-isolation-'+phase+('-v2'if phase=='red-api'else'-v1'),'CASES':{**CASES,'api':engine.CASES['api']}if phase=='red-web'else CASES,'TARGETS':{},'PHASE':phase,'red_qualified':red_qualified}
    exec(compile(runner_source(phase),'<finite independent isolation policy red>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
