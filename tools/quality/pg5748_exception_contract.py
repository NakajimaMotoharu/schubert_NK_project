"""Frozen red/green finite exception constructor tests; no runtime or serialization operations."""
import argparse
import inspect
import re
import pg5732_enum48_selected as previous

CASES={
 'protocol':{'protocol.codec.PayloadGoldenVectorTest'},
 'storage':{'storage.ExceptionValueContractTest'},
 'bootstrap':{'api.file.EnumValueCatalogCompatibilityTest'},
 'api':{'api.idempotency.ExceptionValueContractTest','api.security.ExceptionValueContractTest'},
 'batch':{'batch.cleanup.ExceptionValueContractTest','batch.platform.ExceptionValueContractTest'},
 'web':{'web.logging.ExceptionValueContractTest','web.media.ExceptionValueContractTest','web.messaging.ExceptionValueContractTest','web.revocation.ExceptionValueContractTest','web.security.ExceptionValueContractTest','web.session.ExceptionValueContractTest'}}
TARGETS={
 'storage':['storage/StorageIoException'],
 'api':['api/idempotency/InboxException','api/idempotency/ResponseSnapshotException','api/security/AuthContextCryptoException','api/security/AuthorizationException'],
 'batch':['batch/cleanup/CleanupStoppedException','batch/platform/StopGateException'],
 'web':['web/logging/WebLogPayloadException','web/media/MediaDeliveryException','web/messaging/JmsRequestReplyException','web/messaging/ProtectedReadWireException','web/messaging/ScenarioWireException','web/revocation/RevocationPayloadException','web/security/MqLoginExchangeException','web/security/MqLoginLockedException','web/session/SessionPayloadException']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','green'));parser.add_argument('--version',default='v1');args=parser.parse_args()
    if not re.fullmatch('v[1-9][0-9]*',args.version):raise ValueError('new-only bounded version')
    slot='pg5748-exception-'+args.phase+'-'+args.version
    raw=inspect.getsource(previous.main)
    replacements={
      "'-B','-o','-ntp'":"'-B','-o','-ntp','-fae'",
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'or cls=='web.messaging.ExceptionValueContractTest'else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!=17',
      'len(expected)!=7':'len(expected)!=13',
      "'expectedTests':12":"'expectedTests':17",
      'len(target_counters)==14':'len(target_counters)==16',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(phase=PHASE,executionKind='NORMAL_FINITE_EXCEPTION_PT',purposefulRedEstablished=red_qualified(snapshot,actual,expected,physical,exits,problems)if PHASE=='red'else False)\n    with(out/'manifest.safe.json').open('x')as f:"}
    # No command/scope changes beyond fail-at-end and the exact selected inventory.
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact finite runner predicate')
        raw=raw.replace(old,new,1)
    namespace={**vars(previous),'SLOT':slot,'CASES':CASES,'TARGETS':TARGETS,'PHASE':args.phase,'red_qualified':red_qualified}
    exec(compile(raw,'<finite exception constructor inventory, original Maven failures retained>','exec'),namespace)
    return namespace['main']()


def red_qualified(snapshot,actual,expected,physical,exits,problems):
    import json
    import xml.etree.ElementTree as ET
    prior=json.loads((previous.ROOT.parent/'pgpt-runs/PG379/pg5744-revocation-static-v1/manifest.safe.json').read_bytes())
    sources={p.relative_to(snapshot).as_posix():previous.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    target='dev.codex.schubert.nk.web.messaging.ExceptionValueContractTest'
    wanted=sorted([[target,'exc009NullReasonWithoutCauseIsRejectedAtConstruction'],[target,'exc010NullReasonWithCauseIsRejectedAtConstruction']])
    details=[]
    for path in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        root=ET.parse(path).getroot()
        for case in root.findall('testcase'):
            for item in case.iter():
                if item.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'):return False
            for item in case.findall('failure'):details.append((item.get('type'),item.get('message')))
    return actual==expected and sorted(problems)==wanted and exits==[0,1]and physical==prior['auxClassHashes']and sources==prior['allSourceHashes']and len(details)==2 and all(t=='org.opentest4j.AssertionFailedError'and m=='Expected java.lang.NullPointerException to be thrown, but nothing was thrown.'for t,m in details)


if __name__=='__main__':raise SystemExit(main())
