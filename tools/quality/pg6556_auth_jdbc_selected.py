"""Three own authentication JDBC proxy boundaries; no database, credential file or service."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD = 'ca6268514608106a76314d5167632bde91805f69'
RED_SOURCE = None
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationJdbcBoundary329Test.java'
MAINS = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+n+'.java'
         for n in ('AuthenticationService', 'LoginAttemptRepository')}
TARGETS = {'api': ['api/security/AuthenticationService', 'api/security/LoginAttemptRepository']}
SLOTS = {'red': 'pg6556-auth-jdbc-red-v1', 'green': 'pg6558-auth-jdbc-green-v1'}
METHODS = ('authBoundary329001LockPreservesFatalAfterOwnedStatementClose',
 'authBoundary329002BothRecordOutcomesPreserveFatalWithoutOwningConnection',
 'authBoundary329003AuditFatalCannotBecomeRetryAndAlwaysWipesInput')


def inventory():
    return profile.inventory({'api': {'api.security.AuthenticationJdbcBoundary329Test'}}, (15, 8))


def guard_source(source, phase):
    p = BASE/'PG6554-borrowed-jdbc-qualification-v1/manifest.json'
    if sha(p) != '6346bd42cd80f2d742d49b4f7de907b71a0e5f6d1c13b95c1e52c2e76072fbda':
        raise ValueError('qualified borrowed23 original first')
    q = json.loads(p.read_bytes())
    if q['source'] != OLD or q['actualExit'] != 0: raise ValueError('exact prior Main source')
    changes = set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes != ({TEST} if phase == 'red' else {TEST} | MAINS):
        raise ValueError('one independent Test / two localized Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed build/gates/Current')
    if phase == 'green' and (RED_SOURCE is None or subprocess.check_output(
            ['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('fixed independent red oracle bytes')


def read_red():
    name = 'dev.codex.schubert.nk.api.security.AuthenticationJdbcBoundary329Test'
    message = ('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
               'but was: <dev.codex.schubert.nk.api.security.AuthenticationInfrastructureException>')
    value = original.inspect(W/SLOTS['red'], lambda s: guard_source(s, 'red'), (9, 5),
        {(name, m): message for m in METHODS}, {TEST}, 6)
    print(json.dumps(original.publish(value, BASE/'PG6556-auth-jdbc-original-red-v1')))


def qualify_green():
    run = W/SLOTS['green']; source = json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source, 'green'); cases, _ = inventory()
    return qualify(source, run, cases, (15, 8), MAINS,
        BASE/'PG6554-borrowed-jdbc-qualification-v1/manifest.json',
        '6346bd42cd80f2d742d49b4f7de907b71a0e5f6d1c13b95c1e52c2e76072fbda',
        W/'pg6554-borrowed-jdbc-qualification-v1/manifest.safe.json',
        W/'pg6554-borrowed-jdbc-qualification-v1/findings.safe.json',
        'pg6560-auth-jdbc-qualification-v1', 'PG6560-auth-jdbc-qualification-v1', expected_phase_exits=(0,0,0))


def main():
    p = argparse.ArgumentParser(); p.add_argument('phase', choices=('red','green','read-red','qualify-green'))
    phase = p.parse_args().phase
    if phase == 'read-red': return read_red()
    if phase == 'qualify-green': return qualify_green()
    cases, counts = inventory()
    return profile.execute(SLOTS[phase], lambda s: guard_source(s,phase), cases, counts, (15,8), TARGETS)


if __name__ == '__main__': raise SystemExit(main())
