"""Finite own Web catalog graph proxies and existing receipt/request SQL domains, no real deployment."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='6855dcf9e253599673e57815fc9f408d043d8315'
RED_SOURCE=None
TESTS={
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/receipt/ReceiptFailureGraph329Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/RequestProjectionFailureGraph329Test.java'}
MAINS={
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java'}
TARGETS={'web':['web/receipt/ReceiptReferenceRepository','web/logging/WebRequestLogProducer']}
SLOTS={'red':'pg6600-web-catalog-graph-red-v1','green':'pg6602-web-catalog-graph-green-v1'}


def inventory(phase):
    extra={'web.receipt.ReceiptFailureGraph329Test','web.logging.RequestProjectionFailureGraph329Test'}
    if phase=='green':extra|={'web.receipt.ReceiptReferenceRepositoryTest','web.receipt.ReceiptReferenceFaultTest',
                               'web.logging.WebRequestLogProducerTest','web.bootstrap.WebStartupGraph330Test'}
    return profile.inventory({'web':extra},(18,9) if phase=='red' else (38,13))


def guard_source(source,phase):
    qp=BASE/'PG6598-inspector-qualification-v2/manifest.json'
    if sha(qp)!='4084897514ba3dda64c4b3abd3416fcb0c2c202c6aacc34311ea9a77a4ea8908':raise ValueError('original own60 qualification first')
    q=json.loads(qp.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('qualified Main source identity')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=(TESTS if phase=='red' else TESTS|MAINS):raise ValueError('independent2 Test only or reviewed2 Main PG')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed build/gates/Current')
    if phase=='green' and (RED_SOURCE is None or subprocess.check_output(['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('fixed independent6 and every old Test byte')


def read_red():
    receipt='dev.codex.schubert.nk.web.receipt.ReceiptFailureGraph329Test'
    request='dev.codex.schubert.nk.web.logging.RequestProjectionFailureGraph329Test'
    unexpected=('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
                'but was: <dev.codex.schubert.nk.web.receipt.ReceiptReferenceException>')
    missing='Expected java.lang.AssertionError to be thrown, but nothing was thrown.'
    expected={(receipt,'receipt329001SelectedSqlGraphPreservesFatalAfterOwnedSetupClose'):unexpected,
              (receipt,'receipt329002BothSqlCleanupGraphsCannotDisappearBeforeFixedCatalog'):unexpected,
              (request,'request329001SqlGraphCannotBecomeOrdinaryLocalProjectionFailure'):missing,
              (request,'request329002DisabledSuppressionRollbackGraphKeepsFatalAndStillCloses'):missing}
    value=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(16,7),expected,TESTS,2)
    print(json.dumps(original.publish(value,BASE/'PG6600-web-catalog-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(38,13),MAINS,
        BASE/'PG6598-inspector-qualification-v2/manifest.json',
        '4084897514ba3dda64c4b3abd3416fcb0c2c202c6aacc34311ea9a77a4ea8908',
        W/'pg6598-inspector-qualification-v2/manifest.safe.json',
        W/'pg6598-inspector-qualification-v2/findings.safe.json',
        'pg6604-web-catalog-qualification-v1','PG6604-web-catalog-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','read-red','green','qualify-green'))
    phase=parser.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,
                           (18,9) if phase=='red' else (38,13),TARGETS)


if __name__=='__main__':raise SystemExit(main())
