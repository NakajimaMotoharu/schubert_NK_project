"""Ordinary pure startup/close secondary matrices; not any held recovery operation."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original
import pg6652_consumer_graph_selected as previous

OLD='f16f717d4e5338e7f5b44faef179ada0cf19aae0'
PUBLISHED='0caf68c60c8dac43ecf2b29941deb12a4ff15850'
TESTS={
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ConsumerCleanup333Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyCleanup333Test.java'}
MAINS={p for p in previous.MAINS if not p.endswith('/ArtemisReplyConsumer.java')}
TARGETS={'api':previous.TARGETS['api'],'web':['web/messaging/ArtemisReplyConsumers']}
SLOTS={'red-api':'pg6680-consumer-cleanup-api-red-v1','red-web':'pg6682-consumer-cleanup-web-red-v1','green':'pg6684-consumer-cleanup-green-v1'}
EXPECTED={'red-api':(16,8),'red-web':(14,8),'green':(83,22)}


def inventory(phase):
    if phase=='green':
        extra,_=previous.inventory('green')
        extra['api'].add('api.messaging.inbound.ConsumerCleanup333Test')
        extra['web'].add('web.messaging.ReplyCleanup333Test')
    else:
        extra={'api':{'api.messaging.inbound.ConsumerCleanup333Test'}} if phase=='red-api' else {'web':{'web.messaging.ReplyCleanup333Test'}}
    return profile.inventory(extra,EXPECTED[phase])


def guard_source(source,phase):
    qp=BASE/'PG6668-current4170-cases/qualification.json'
    if sha(qp)!='75a039af0e96adace67974c93354cfc175bfe1063b3ddb30908f3a3ad7894c45':raise ValueError('genuine original4170 prerequisite')
    q=json.loads(qp.read_bytes())
    if not(q['productionSource']==OLD and q['actualExit']==q['FESFlakyNotRun']==0 and (q['tests'],q['suites'],q['mainClasses'])==(4170,638,1667)):
        raise ValueError('original complete source and physical baseline')
    subprocess.check_call(['git','merge-base','--is-ancestor',PUBLISHED,'origin/main'],cwd=ROOT)
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=(TESTS if phase.startswith('red') else TESTS|MAINS):raise ValueError('two independent Tests / four necessary Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('quality/build/Current fixed')
    if phase=='green':
        reds=[json.loads((W/SLOTS[p]/'begin.safe.json').read_bytes())['source'] for p in ('red-api','red-web')]
        if reds[0]!=reds[1] or subprocess.check_output(['git','diff',reds[0],source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):raise ValueError('both red sources and all new/old Test bytes fixed')


def read_red(phase):
    api=phase=='red-api'
    cls='dev.codex.schubert.nk.'+('api.messaging.inbound.ConsumerCleanup333Test' if api else 'web.messaging.ReplyCleanup333Test')
    if api:
        names=('clean333001SyncStartupSecondaryAfterEveryOwnedClose','clean333002WebLogStartupSecondaryAfterOwnedClose','clean333003QuestionStartupSecondaryAfterOwnedClose')
        expected={(cls,n):'CONS333-'+str(i)+' startup secondary after all closes ==> expected: <true> but was: <false>' for i,n in enumerate(names)}
        expected[cls,'clean333004SyncMultiClosePreservesDeferredFatalAndSuccessfulPhases']='CONS333-4 deferred fatal after four closes ==> expected: <true> but was: <false>'
    else:
        expected={(cls,'clean333005ReplyStartupNoSuppSecondaryAfterSingleClose'):'CONS333-5 reply secondary after close ==> expected: <true> but was: <false>'}
    value=original.inspect(W/SLOTS[phase],lambda s:guard_source(s,phase),(10,5) if api else (12,6),expected,TESTS,6 if api else 2)
    print(json.dumps(original.publish(value,BASE/('PG6680-cleanup-api-original-red-v1' if api else 'PG6682-cleanup-web-original-red-v1'))))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,EXPECTED['green'],MAINS,
      BASE/'PG6666-consumer-graph-qualification-v2/manifest.json',
      'dc608c847f6f03f31adabdb70b1fc28366472ae77d5c18f36c9a29f518de2edd',
      W/'pg6666-consumer-graph-qualification-v2/manifest.safe.json',
      W/'pg6666-consumer-graph-qualification-v2/findings.safe.json',
      'pg6686-consumer-cleanup-qualification-v1','PG6686-consumer-cleanup-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=(*SLOTS,'read-api','read-web','qualify-green'))
    phase=parser.parse_args().phase
    if phase.startswith('read-'):return read_red('red-'+phase.removeprefix('read-'))
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,EXPECTED[phase],TARGETS)


if __name__=='__main__':raise SystemExit(main())
