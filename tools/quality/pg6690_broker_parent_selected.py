"""Ordinary owned interface/configuration fixtures; no real credential, VM or recovery action."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original
import pg6680_consumer_cleanup_selected as previous

OLD='903b8b93f3d46efa90546c62cd4f10234c33520f'
PUBLISHED='b6f09c9a2cf918656e8b0500896ce963d6512257'
TESTS={
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/BrokerGraph334Test.java',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ParentGraph334Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/BrokerGraph334Test.java'}
MAINS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ArtemisConnectionFactoryProvider.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/ApiMessagingRuntime.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java'}
TARGETS={'api':['api/messaging/config/ApiBrokerContexts','api/messaging/config/ArtemisConnectionFactoryProvider','api/messaging/inbound/ApiMessagingRuntime'],
         'web':['web/messaging/WebBrokerContexts']}
SLOTS={'red-api':'pg6698-broker-api-red-v2','red-web':'pg6700-broker-web-red-v2','green':'pg6702-broker-parent-green-v2'}
EXPECTED={'red-api':(17,9),'red-web':(15,8),'green':(127,33)}


def inventory(phase):
    if phase=='green':
        extra,_=previous.inventory('green')
        extra['api']|={'api.messaging.config.BrokerGraph334Test','api.messaging.inbound.ParentGraph334Test',
            'api.messaging.config.ApiBrokerContextsTest','api.messaging.config.ArtemisConnectionFactoryProviderTest',
            'api.messaging.config.ApiFactoryOwnershipTest','api.messaging.config.ApiFactoryNativeRetentionTest','api.messaging.inbound.ApiMessagingRuntimeTest'}
        extra['web']|={'web.messaging.BrokerGraph334Test','web.messaging.WebBrokerContextsTest',
            'web.messaging.WebBrokerFactoryOwnershipTest','web.messaging.WebFactoryNativeRetentionTest'}
    elif phase=='red-api':extra={'api':{'api.messaging.config.BrokerGraph334Test','api.messaging.inbound.ParentGraph334Test'}}
    else:extra={'web':{'web.messaging.BrokerGraph334Test'}}
    return profile.inventory(extra,EXPECTED[phase])


def guard_source(source,phase):
    qp=BASE/'PG6686-consumer-cleanup-qualification-v1/manifest.json'
    if sha(qp)!='8e52123141aa8acd8cfa9da8e46966824dbb6bafa8959118ebc1870fff6989f5':raise ValueError('genuine original83 first')
    q=json.loads(qp.read_bytes())
    if not(q['source']==OLD and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(83,22,1667)):raise ValueError('original83 source/Main baseline')
    subprocess.check_call(['git','merge-base','--is-ancestor',PUBLISHED,'origin/main'],cwd=ROOT)
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=(TESTS if phase.startswith('red') else TESTS|MAINS):raise ValueError('three independent Test files / four necessary Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('quality/build/Current fixed')
    if phase=='green':
        reds=[json.loads((W/SLOTS[p]/'begin.safe.json').read_bytes())['source'] for p in ('red-api','red-web')]
        if reds[0]!=reds[1] or subprocess.check_output(['git','diff',reds[0],source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):raise ValueError('both red sources and all Test bytes fixed')


def read_red(phase):
    api=phase=='red-api';prefix='dev.codex.schubert.nk.'
    if api:
        cls=prefix+'api.messaging.config.BrokerGraph334Test'
        expected={(cls,n):msg+' ==> expected: <true> but was: <false>' for n,msg in (
            ('fact334001ApiOpenPreRedactionAndCopyCleanup','FACT334001 fatal before API redaction'),
            ('fact334002ApiMultiOwnerCloseRetainsLateGraphAndSuccessfulPhases','FACT334002 late API graph after all close attempts'),
            ('fact334003ApiPartialConstructionClassifiesOnlyUnretainedSecondaryAfterAllClose','FACT334003 unretained graph after reverse partial close'),
            ('fact334004ApiFactoryNoSuppSecondaryAfterOwnedClose','FACT334004 API factory graph after owned close'))}
        expected[prefix+'api.messaging.inbound.ParentGraph334Test','fact334005ParentNotificationAndGroupCloseAfterCleanup']='FACT334005 parent notification after cleanup ==> expected: <true> but was: <false>'
    else:
        cls=prefix+'web.messaging.BrokerGraph334Test'
        expected={(cls,n):msg+' ==> expected: <true> but was: <false>' for n,msg in (
            ('fact334006WebOpenPreRedactionAndCopyCleanup','FACT334006 fatal before Web redaction'),
            ('fact334007WebCloseTraversesLinkedGraphAndRetainsRetryPhase','FACT334007 Web linked graph after owned close'),
            ('fact334008WebFactoryNoSuppSecondaryAfterOwnedClose','FACT334008 Web factory graph after owned close'))}
    value=original.inspect(W/SLOTS[phase],lambda s:guard_source(s,phase),(11,6) if api else (13,6),expected,TESTS,6 if api else 2)
    print(json.dumps(original.publish(value,BASE/('PG6698-broker-api-original-red-v2' if api else 'PG6700-broker-web-original-red-v2'))))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,EXPECTED['green'],MAINS,
      BASE/'PG6686-consumer-cleanup-qualification-v1/manifest.json',
      '8e52123141aa8acd8cfa9da8e46966824dbb6bafa8959118ebc1870fff6989f5',
      W/'pg6686-consumer-cleanup-qualification-v1/manifest.safe.json',
      W/'pg6686-consumer-cleanup-qualification-v1/findings.safe.json',
      'pg6704-broker-parent-qualification-v2','PG6704-broker-parent-qualification-v2',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=(*SLOTS,'read-api','read-web','qualify-green'))
    phase=parser.parse_args().phase
    if phase.startswith('read-'):return read_red('red-'+phase.removeprefix('read-'))
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,EXPECTED[phase],TARGETS)


if __name__=='__main__':raise SystemExit(main())
