"""Normal finite14 red/green, original failures retained; no real JMS/DB/VM operation."""
import argparse
import inspect
import json
import xml.etree.ElementTree as ET
import pg5732_enum48_selected as previous

CASES={**previous.CASES,'api':{'api.messaging.inbound.InboundTransactionsPrimaryContractTest'},'web':{'web.messaging.ReplyIsolationPrimaryContractTest'}}
TARGETS={'api':['api/messaging/inbound/InboundTransactions'],'web':['web/messaging/ArtemisReplyConsumer']}
RED={
 ('dev.codex.schubert.nk.api.messaging.inbound.InboundTransactionsPrimaryContractTest','jmsP001SameRollbackFailureNeverSelfSuppresses'),
 ('dev.codex.schubert.nk.api.messaging.inbound.InboundTransactionsPrimaryContractTest','jmsP004SameProtocolIsolationFailureRemainsOriginalAndUncommitted'),
 ('dev.codex.schubert.nk.web.messaging.ReplyIsolationPrimaryContractTest','jmsP006SameProtocolIsolationFailureNeverSelfSuppressesOrCommits')}


def red_qualified(snapshot,actual,expected,physical,exits,problems,phase):
    p=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5754-current3932-cases/qualification.json'
    prior=json.loads(p.read_bytes());static=json.loads((previous.ROOT.parent/'pgpt-runs/PG379/pg5750-exception-static-v1/manifest.safe.json').read_bytes())
    sources={p.relative_to(snapshot).as_posix():previous.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};details=[]
    for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        for case in ET.parse(p).getroot().findall('testcase'):
            if any(c.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for c in case.iter()):return False
            for failure in case.findall('failure'):details.append((failure.get('type'),failure.get('message')))
    wanted={p for p in RED if '.web.'in p[0]}if phase=='red-web'else RED
    return actual==expected and {tuple(p)for p in problems}==wanted and exits==[0,1]and sources==static['allSourceHashes']and physical==prior['allPhysicalMainSha256']and len(details)==len(wanted)and all(t=='org.opentest4j.AssertionFailedError'and'IllegalArgumentException'in m for t,m in details)


def runner_source(phase='green'):
    raw=inspect.getsource(previous.main)
    changes={
      "'-B','-o','-ntp'":"'-B','-o','-ntp','-fae'",
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'else 1 if module=='api'and PHASE=='red-web'else 5 if module=='api'else 2 if module=='web'else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!='+str(10 if phase=='red-web'else 14),
      "'expectedTests':12":"'expectedTests':"+str(10 if phase=='red-web'else 14),
      'len(target_counters)==14':'len(target_counters)==2',
      '    done=done and target100':'    # This selected finite fixture reports actual counters; full-class100 remains a separate whole/native requirement.',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(phase=PHASE,executionKind='NORMAL_FINITE_JMS_PRIMARY_PT',purposefulRedEstablished=red_qualified(snapshot,actual,expected,physical,exits,problems,PHASE)if PHASE.startswith('red')else False,targetFour100RequiredBeforeProgramCompletion=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact finite runner predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite14 original-exit selected reader>','exec')
    return raw


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','red-web','green'));args=parser.parse_args()
    if args.phase=='red':raise ValueError('original API red already issued; read original only, no repeat')
    slot='pg5774-jms-primary-'+args.phase+('-v2'if args.phase=='red-web'else'-v1')
    cases={**CASES,'api':previous.CASES['api']}if args.phase=='red-web'else CASES
    namespace={**vars(previous),'SLOT':slot,'CASES':cases,'TARGETS':TARGETS,'PHASE':args.phase,'red_qualified':red_qualified}
    exec(compile(runner_source(args.phase),'<finite selected not runtime verification>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
