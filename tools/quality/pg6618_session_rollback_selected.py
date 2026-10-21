"""Own proxy before session creation; no identity/CSRF issuance, DB, VM or credential operation."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='78f4a54fa340bacfcc8ba5528348276b5c3209da'
RED_SOURCE='93f1410684a8d515bc602dd787b3063ddd690547'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionRollbackAttachment329Test.java'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository.java'
TARGETS={'web':['web/session/EncryptedWebSessionRepository']}
SLOTS={'red':'pg6618-session-rollback-red-v1','green':'pg6620-session-rollback-green-v1'}


def inventory(phase):
    extra={'web.session.SessionRollbackAttachment329Test'}
    if phase=='green':extra|={'web.session.EncryptedWebSessionRepositoryTest','web.session.SessionFailureGraphTest',
                               'web.session.SessionJdbcGraph328Test','web.bootstrap.WebStartupGraph330Test'}
    return profile.inventory({'web':extra},(15,8) if phase=='red' else (33,12))


def guard_source(source,phase):
    path=BASE/'PG6616-web-owned-qualification-v1/manifest.json'
    if sha(path)!='bccc7b2280dbebd914cc5da16f0c5362c6e3d11df6413718ec9de47ada451018':raise ValueError('original qualified39 first')
    q=json.loads(path.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('qualified Main baseline identity')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=({TEST} if phase=='red' else {TEST,MAIN}):raise ValueError('one independent Test / one reviewed attachment Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('fixed gates/build/Current')
    if phase=='green' and (RED_SOURCE is None or subprocess.check_output(['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('all original three/old Test oracle bytes fixed')


def read_red():
    key=('dev.codex.schubert.nk.web.session.SessionRollbackAttachment329Test',
         'session329001DisabledPrimaryCannotLoseRollbackFatalBeforeOwnedClose')
    message=('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
             'but was: <dev.codex.schubert.nk.web.session.SessionStoreException>')
    value=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(13,6),{key:message},{TEST},2)
    print(json.dumps(original.publish(value,BASE/'PG6618-session-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(33,12),{MAIN},
        BASE/'PG6616-web-owned-qualification-v1/manifest.json',
        'bccc7b2280dbebd914cc5da16f0c5362c6e3d11df6413718ec9de47ada451018',
        W/'pg6616-web-owned-qualification-v1/manifest.safe.json',
        W/'pg6616-web-owned-qualification-v1/findings.safe.json',
        'pg6622-session-rollback-qualification-v1','PG6622-session-rollback-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','read-red','green','qualify-green'))
    phase=parser.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,(15,8) if phase=='red' else (33,12),TARGETS)


if __name__=='__main__':raise SystemExit(main())
