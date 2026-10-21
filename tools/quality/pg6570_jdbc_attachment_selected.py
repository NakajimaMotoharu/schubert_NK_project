"""Adopt already-qualified pure secondary port in one owned JDBC transaction, fixed oracle."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='e033db0f806549a20adb01e788f5d1d5e2d73d92'
RED_SOURCE='9f801319f097f323c24d8597167887d5bda0a78a'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/JdbcRollbackAttachment330Test.java'
MAINS={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java'}
TARGETS={'api':['api/dispatch/JdbcSyncRequestProcessor','api/error/TemporaryInfrastructureException']}
SLOTS={'red':'pg6570-jdbc-attachment-red-v1','green':'pg6572-jdbc-attachment-green-v1'}


def inventory(phase):
    extra={'api.dispatch.JdbcRollbackAttachment330Test'}
    if phase=='green':extra|={'api.dispatch.JdbcTransactionFatal329Test',
        'api.dispatch.JdbcTransactionBoundary329Test','api.error.TemporaryFailureGraph329Test',
        'api.error.ApiStartupGraph330Test'}
    return profile.inventory({'api':extra},(15,8) if phase=='red' else (31,12))


def guard_source(source,phase):
    p=BASE/'PG6568-readiness-qualification-v1/manifest.json'
    if sha(p)!='f0d030122e89465916d435906aeb0d7796ec1ba721ccaa79e0fc226605945431':
        raise ValueError('original qualified330 ports first')
    q=json.loads(p.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('exact qualified Main source')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=({TEST} if phase=='red' else {TEST}|MAINS):raise ValueError('one independent Test / one owner Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed gates/build/Current')
    if phase=='green' and (RED_SOURCE is None or subprocess.check_output(
            ['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('fixed independent red and all existing Test bytes')


def read_red():
    key=('dev.codex.schubert.nk.api.dispatch.JdbcRollbackAttachment330Test',
         'attachment330001DisabledPrimaryCannotLoseRollbackFatalAndMustClose')
    message=('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
             'but was: <dev.codex.schubert.nk.api.error.TemporaryInfrastructureException>')
    value=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(9,5),{key:message},{TEST},6)
    print(json.dumps(original.publish(value,BASE/'PG6570-jdbc-attachment-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(31,12),MAINS,
        BASE/'PG6568-readiness-qualification-v1/manifest.json',
        'f0d030122e89465916d435906aeb0d7796ec1ba721ccaa79e0fc226605945431',
        W/'pg6568-readiness-qualification-v1/manifest.safe.json',
        W/'pg6568-readiness-qualification-v1/findings.safe.json',
        'pg6574-jdbc-attachment-qualification-v1','PG6574-jdbc-attachment-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=('red','green','read-red','qualify-green'))
    phase=p.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,
                           (15,8) if phase=='red' else (31,12),TARGETS)


if __name__=='__main__':raise SystemExit(main())
