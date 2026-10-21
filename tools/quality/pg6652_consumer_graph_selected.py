"""Finite owned ordinary JMS proxies; never a Root/VM/cohort/permit operation."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='164f1d9b7566053a1e1a210d140e1d941430dfdb'
PUBLISHED='9cca2275bef6ffb29d96d623e7637b61e05d3d58'
TESTS={
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ConsumerGraph332Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyConsumerGraph332Test.java'}
MAINS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'+n+'.java'
 for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers')
}|{'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'+n+'.java'
   for n in ('ArtemisReplyConsumer','ArtemisReplyConsumers')}
TARGETS={'api':['api/messaging/inbound/'+n for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers')],
         'web':['web/messaging/ArtemisReplyConsumer','web/messaging/ArtemisReplyConsumers']}
SLOTS={'red-api':'pg6652-consumer-api-red-v1','red-web':'pg6654-consumer-web-red-v1','green':'pg6656-consumer-graph-green-v1'}
EXPECTED={'red-api':(16,8),'red-web':(16,8),'green':(77,20)}


def inventory(phase):
    extra={}
    if phase in ('red-api','green'):extra['api']={'api.messaging.inbound.ConsumerGraph332Test'}
    if phase in ('red-web','green'):extra['web']={'web.messaging.ReplyConsumerGraph332Test'}
    if phase=='green':
        extra['api']|={'api.messaging.inbound.'+n for n in ('SyncRequestConsumersTest','WebLogConsumersTest','QuestionWorkConsumersTest','ConfirmedRollbackCallbackTest','ConsumerRollbackUnconfirmedContractTest')}
        extra['api'].add('api.error.TemporaryFailureGraph329Test')
        extra['web']|={'web.messaging.'+n for n in ('ArtemisReplyConsumersTest','ArtemisReplyConsumerTest','ReplyRollbackSignalContractTest','ReplyRollbackUnconfirmedContractTest')}
        extra['web'].add('web.bootstrap.WebStartupGraph330Test')
    return profile.inventory(extra,EXPECTED[phase])


def guard_source(source,phase):
    q=BASE/'PG6650-local-audit-qualification-v1/manifest.json'
    if sha(q)!='0f3beb9b42cf6c40b3a30aac55331507ea4805ce231bd82d7fd80317146d4f8b':raise ValueError('original local31 prerequisite')
    if json.loads(q.read_bytes())['source']!=OLD:raise ValueError('qualified current Main baseline')
    subprocess.check_call(['git','merge-base','--is-ancestor',PUBLISHED,'origin/main'],cwd=ROOT)
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=(TESTS if phase.startswith('red') else TESTS|MAINS):raise ValueError('two new Test / five necessary Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('quality/build/Current fixed')
    if phase=='green':
        reds=[json.loads((W/SLOTS[p]/'begin.safe.json').read_bytes())['source'] for p in ('red-api','red-web')]
        if reds[0]!=reds[1] or subprocess.check_output(['git','diff',reds[0],source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):raise ValueError('both red sources and all Test bytes fixed')


def read_red(phase):
    api=phase=='red-api'
    cls='dev.codex.schubert.nk.'+('api.messaging.inbound.ConsumerGraph332Test' if api else 'web.messaging.ReplyConsumerGraph332Test')
    names=(('cons332001SyncCannotRetryConfirmedRollbackWithFatalGraph','cons332002WebLogCannotRetryConfirmedRollbackWithFatalGraph','cons332003QuestionCannotRetryConfirmedRollbackWithFatalGraph') if api else
           ('cons332005WrappedFatalSignalsThenRethrowsOriginalWithoutSecondRollback','cons332006PreflightIsNotConfirmedAndStateResetsPerDelivery','cons332007RollbackFatalIsNeverReissuedAndNotificationCannotMaskIt','cons332008OrdinaryCycleDirectFatalAndPublicListenerContractsRemain'))
    expected={(cls,n):'expected: <true> but was: <false>' for n in names}
    value=original.inspect(W/SLOTS[phase],lambda s:guard_source(s,phase),(10,5) if api else (14,6),expected,TESTS,6 if api else 2)
    print(json.dumps(original.publish(value,BASE/('PG6652-consumer-api-original-red-v1' if api else 'PG6654-consumer-web-original-red-v1'))))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,EXPECTED['green'],MAINS,
      BASE/'PG6650-local-audit-qualification-v1/manifest.json',
      '0f3beb9b42cf6c40b3a30aac55331507ea4805ce231bd82d7fd80317146d4f8b',
      W/'pg6650-local-audit-qualification-v1/manifest.safe.json',
      W/'pg6650-local-audit-qualification-v1/findings.safe.json',
      'pg6658-consumer-graph-qualification-v1','PG6658-consumer-graph-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=(*SLOTS,'read-api','read-web','qualify-green'))
    phase=parser.parse_args().phase
    if phase.startswith('read-'):return read_red('red-'+phase.removeprefix('read-'))
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,EXPECTED[phase],TARGETS)


if __name__=='__main__':raise SystemExit(main())
