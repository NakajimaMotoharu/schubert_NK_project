"""Own pure JDBC fixture across two Web manual owners; normal domains remain fixed."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='d48a13f4d36fe51bd5a333d0d0d926b76d1e280a'
RED_SOURCE='dbb0a503b1e778a87a895c24352c3d00a33b88c2'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebOwnedAttachment329Test.java'
MAINS={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'+p+'.java' for p in
       ('logging/WebLogDispatcher','revocation/RevocationRetryCoordinator')}
TARGETS={'web':['web/logging/WebLogDispatcher','web/revocation/RevocationRetryCoordinator']}
SLOTS={'red':'pg6612-web-owned-attachment-red-v1','green':'pg6614-web-owned-attachment-green-v1'}


def inventory(phase):
    extra={'web.logging.WebOwnedAttachment329Test'}
    if phase=='green':extra|={'web.logging.WebLogDispatcherTest','web.revocation.RevocationRetryCoordinatorTest','web.bootstrap.WebStartupGraph330Test'}
    return profile.inventory({'web':extra},(18,8) if phase=='red' else (39,11))


def guard_source(source,phase):
    p=BASE/'PG6610-web-catalog-qualification-v2/manifest.json'
    if sha(p)!='d4fece4a19343ddd594239e10dee955664e7f6fc0bb8c49aa1d9b5f02ce51186':raise ValueError('genuine original38 qualification first')
    q=json.loads(p.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('exact qualified baseline Main')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=({TEST} if phase=='red' else {TEST}|MAINS):raise ValueError('one pure fixture Test / necessary2 manual owner Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('fixed gates/build/Current')
    if phase=='green' and (RED_SOURCE is None or subprocess.check_output(['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('all independent original6/old Test bytes fixed')


def read_red():
    cls='dev.codex.schubert.nk.web.logging.WebOwnedAttachment329Test'
    names=('owned329001DispatcherRollbackGraphSurvivesDisabledSuppression',
           'owned329002DispatcherCloseGraphSurvivesAndNonFatalRawSqlRemainsSame',
           'owned329004RevocationRollbackGraphCannotSkipRemainingClose',
           'owned329005RevocationCloseGraphAndBothFatalGraphsKeepPrimary')
    expected={(cls,name):'expected: <true> but was: <false>' for name in names}
    expected[(cls,'owned329003DispatcherDirectErrorRollsBackAndKeepsLegacyClosePriority')]='expected: <1> but was: <0>'
    value=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(16,6),expected,{TEST},2)
    print(json.dumps(original.publish(value,BASE/'PG6612-web-owned-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(39,11),MAINS,
        BASE/'PG6610-web-catalog-qualification-v2/manifest.json',
        'd4fece4a19343ddd594239e10dee955664e7f6fc0bb8c49aa1d9b5f02ce51186',
        W/'pg6610-web-catalog-qualification-v2/manifest.safe.json',
        W/'pg6610-web-catalog-qualification-v2/findings.safe.json',
        'pg6616-web-owned-qualification-v1','PG6616-web-owned-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','read-red','green','qualify-green'))
    phase=parser.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,(18,8) if phase=='red' else (39,11),TARGETS)


if __name__=='__main__':raise SystemExit(main())
