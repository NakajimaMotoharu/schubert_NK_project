"""Pure provider graphs, then existing owned local domains; no Root/VM/remote actions."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='d25fcb3f487395f83cdfd0df9ff934812f5fd9b3'
TESTS={
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxSecondary330Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/JmsSecondary330Test.java'}
MAINS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogMessageSender.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisRequestSender.java'}
TARGETS={'api':['api/messaging/outbound/OutboxJmsSender'],
         'web':['web/logging/WebLogMessageSender','web/messaging/ArtemisRequestSender']}
SLOTS={'red-api':'pg6626-jms-secondary-api-red-v1','red-web':'pg6628-jms-secondary-web-red-v1',
       'green':'pg6630-jms-secondary-green-v1'}
EXPECTED={'red-api':(15,8),'red-web':(18,8),'green':(86,17)}


def inventory(phase):
    extra={}
    if phase in ('red-api','green'):extra['api']={'api.messaging.outbound.OutboxSecondary330Test'}
    if phase in ('red-web','green'):extra['web']={'web.logging.JmsSecondary330Test'}
    if phase=='green':
        extra['api']|={'api.messaging.outbound.OutboxFailureOwnershipTest','api.messaging.outbound.OutboxDispatcherTest',
                       'api.messaging.outbound.OwnedOutboxDispatcherTest','api.error.TemporaryFailureGraph329Test'}
        extra['web']|={'web.logging.WebLogMessageSenderTest','web.logging.WebLogDispatcherTest',
                       'web.messaging.ArtemisRequestSenderTest','web.bootstrap.WebStartupGraph330Test'}
    return profile.inventory(extra,EXPECTED[phase])


def guard_source(source,phase):
    path=BASE/'PG6622-session-rollback-qualification-v1/manifest.json'
    if sha(path)!='4e5fd0ed47bceff1014267a8782b6319981b16e34b1a9e398c0b7b9cca107b67':raise ValueError('original qualified33 baseline')
    old=json.loads(path.read_bytes())
    if old['source']!=OLD or old['actualExit']!=0:raise ValueError('qualified Main baseline')
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=(TESTS if phase.startswith('red') else TESTS|MAINS):raise ValueError('two new Test / three necessary sender Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('unchanged quality/build/Current')
    if phase=='green':
        sources=[json.loads((W/SLOTS[p]/'begin.safe.json').read_bytes())['source'] for p in ('red-api','red-web')]
        if sources[0]!=sources[1] or subprocess.check_output(['git','diff',sources[0],source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):
            raise ValueError('both original reds and all old/new Test bytes fixed')


def read_red(phase):
    cls='dev.codex.schubert.nk.'+('api.messaging.outbound.OutboxSecondary330Test' if phase=='red-api' else 'web.logging.JmsSecondary330Test')
    names=(('jms330001DisabledPrimaryRetainsRollbackFatalThroughFinalDisposition',
            'jms330002DuplicateCannotConfirmSuccessBeforeRollbackFatalClassification') if phase=='red-api' else
           ('jms330004LogDisabledPrimaryCannotLoseRollbackOrCloseFatal',
            'jms330005LogDuplicateCannotHideRollbackFatalAndDirectCloseStillWins',
            'jms330007RequestRetainsDisabledPrimaryRollbackFatalAfterOwnedClose',
            'jms330008RequestClassifiesCloseGraphAfterModeFailureOrSuccessfulCommit'))
    expected={(cls,n):'expected: <true> but was: <false>' for n in names}
    value=original.inspect(W/SLOTS[phase],lambda s:guard_source(s,phase),(9,5) if phase=='red-api' else (16,6),expected,TESTS,6 if phase=='red-api' else 2)
    name='PG6626-jms-api-original-red-v1' if phase=='red-api' else 'PG6628-jms-web-original-red-v1'
    print(json.dumps(original.publish(value,BASE/name)))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,EXPECTED['green'],MAINS,
      BASE/'PG6622-session-rollback-qualification-v1/manifest.json',
      '4e5fd0ed47bceff1014267a8782b6319981b16e34b1a9e398c0b7b9cca107b67',
      W/'pg6622-session-rollback-qualification-v1/manifest.safe.json',
      W/'pg6622-session-rollback-qualification-v1/findings.safe.json',
      'pg6632-jms-secondary-qualification-v1','PG6632-jms-secondary-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=(*SLOTS,'read-api','read-web','qualify-green'))
    phase=parser.parse_args().phase
    if phase.startswith('read-'):return read_red('red-'+phase.removeprefix('read-'))
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,EXPECTED[phase],TARGETS)


if __name__=='__main__':raise SystemExit(main())
