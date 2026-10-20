"""Four finite memory-only terminal-admission reds, original851/1666 Main unchanged."""
import argparse
import inspect
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
import pg5732_enum48_selected as engine

API_CLASS='dev.codex.schubert.nk.api.messaging.inbound.CommittedTerminalAdmissionContractTest'
WEB_CLASS='dev.codex.schubert.nk.web.messaging.ReplyCommittedTerminalAdmissionContractTest'
RED_API={(API_CLASS,m)for m in('term001SyncCommitStopsAllFourContextAdmissions','term002QuestionCommitStopsFurtherAdmissions','term003WebLogCommitStopsFurtherAdmissions')}
RED_WEB={(WEB_CLASS,'term004ReplyCommitStopsFurtherAdmissions')}
CASES={**engine.CASES,'api':{'api.messaging.inbound.CommittedTerminalAdmissionContractTest'},'web':{'web.messaging.ReplyCommittedTerminalAdmissionContractTest'}}


def expected_assertions(message,method):
    actual=Counter(re.findall(r'expected: <([^>]+)> but was: <([^>]+)>',message or''))
    return actual==Counter({('1','5'if method=='term001SyncCommitStopsAllFourContextAdmissions'else'2'):3})


def red_qualified(snapshot,actual,expected,physical,exits,problems,phase):
    base=engine.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5848-protocol-expression-static-v1/manifest.json';private=engine.ROOT.parent/'pgpt-runs/PG379/pg5848-protocol-expression-static-v1/manifest.safe.json'
    if engine.sha(sp)!='3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100'or engine.sha(private)!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('original862 complete Main proof')
    proof=json.loads(private.read_bytes());sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};wanted=RED_API if phase=='red-api'else RED_WEB
    inventory={k:v for k,v in expected.items()if phase!='red-api'or'.web.'not in k};classes={k:v for k,v in proof['auxClassHashes'].items()if phase!='red-api'or not k.startswith('web:')};failures=[]
    for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        for case in ET.parse(p).getroot().findall('testcase'):
            if any(n.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in case.iter()):return False
            for failure in case.findall('failure'):
                method=case.get('name','').removesuffix('()')
                if failure.get('type')not in('org.opentest4j.AssertionFailedError','org.opentest4j.MultipleFailuresError')or not expected_assertions(failure.get('message'),method):return False
                failures.append((case.get('classname'),method))
    return sources==proof['allSourceHashes']and physical==classes and actual==inventory and exits==[0,1]and {tuple(r)for r in problems}==wanted and set(failures)==wanted and len(failures)==len(wanted)


def runner_source(phase):
    raw=inspect.getsource(engine.main);count=11 if phase=='red-api'else 9
    changes={
      "'-B','-o','-ntp'":"'-B','-o','-ntp','-fae'",
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'or(module=='api'and PHASE=='red-api')else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!='+str(count),
      "'expectedTests':12":"'expectedTests':"+str(count),
      'len(physical)==1664':'len(physical)==1666','len(target_counters)==14':'len(target_counters)==0',
      '    done=exits==[0,0]':'    target100=False # no empty target coverage credit\n    done=exits==[0,0]',
      '    done=done and target100':'    # Purposeful reds are never PT PASS or coverage success.',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(phase=PHASE,executionKind='NORMAL_COMMITTED_TERMINAL_POLICY_RED',purposefulRedEstablished=red_qualified(snapshot,actual,expected,physical,exits,problems,PHASE),webNotRunRetained=PHASE=='red-api',noRuntimeOrVmOperation=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact terminal red predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite committed terminal red>','exec');return raw


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=('red-api','red-web'));phase=p.parse_args().phase
    scope={**vars(engine),'SLOT':'pg5854-terminal-'+phase+'-v1','CASES':{**CASES,'api':engine.CASES['api']}if phase=='red-web'else CASES,'TARGETS':{},'PHASE':phase,'red_qualified':red_qualified}
    exec(compile(runner_source(phase),'<finite terminal admission red>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
