"""SSC328 pure ordinary JDBC graph: separate failing API/Web originals, fixed-oracle green."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
import finite_selected_profile as profile

OLD = 'f39de2986cbe0dc4a552f64d55ac723002cc77f6'
RED_SOURCE = None
TESTS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationJdbcGraph328Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionJdbcGraph328Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/revocation/RevocationJdbcGraph328Test.java'}
MAINS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationInfrastructureException.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator.java'}
API = {'api': {'api.security.AuthenticationFailureGraphTest', 'api.security.AuthenticationJdbcGraph328Test'}}
WEB = {'web': {'web.session.SessionFailureGraphTest', 'web.session.SessionJdbcGraph328Test',
               'web.revocation.RevocationJdbcGraph328Test'}}
PROFILES = {
 'api-red': ('pg6534-jdbc-api-red-v1', (16, 9), API, {'api': ['api/security/AuthenticationInfrastructureException']}),
 'web-red': ('pg6536-jdbc-web-red-v1', (19, 10), WEB,
             {'web': ['web/session/SessionStoreException', 'web/revocation/RevocationRetryCoordinator']}),
 'green': ('pg6538-jdbc-graph-green-v1', (23, 12), {**API, **WEB},
           {'api': ['api/security/AuthenticationInfrastructureException'],
            'web': ['web/session/SessionStoreException', 'web/revocation/RevocationRetryCoordinator']})}


def inventory(phase):
    _, counts, extra, _ = PROFILES[phase]
    return profile.inventory(extra, counts)


def guard_source(source, phase):
    qp = BASE/'PG6524-current4073-cases/qualification.json'
    if sha(qp) != '411c8764bba9ae6fa01c24d27c2b4f2cacf02686b568d9d1d6912cc5ef4da936':
        raise ValueError('immutable original4073 qualification first')
    q = json.loads(qp.read_bytes())
    if not (q['productionSource'] == OLD and q['actualExit'] == 0
            and q['returnedOriginalTerminalExact'] and q['FESFlakyNotRun'] == 0
            and (q['tests'], q['suites'], q['mainClasses']) == (4073, 614, 1667)):
        raise ValueError('genuine original4073, not begin or another source')
    changes = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'],
                                          cwd=ROOT, text=True).splitlines())
    if changes != (TESTS | MAINS if phase == 'green' else TESTS):
        raise ValueError('old Main plus independent9(red), localized three Main and fixed9(green)')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw',
                               'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current unchanged')
    if phase == 'green':
        if RED_SOURCE is None or subprocess.check_output(['git', 'diff', RED_SOURCE, source, '--',
                ':(glob)src/*/src/test/**'], cwd=ROOT):
            raise ValueError('independent red Test bytes fixed before PG')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=tuple(PROFILES))
    phase = parser.parse_args().phase
    slot, expected, _, targets = PROFILES[phase]
    cases, counts = inventory(phase)
    return profile.execute(slot, lambda source: guard_source(source, phase), cases, counts, expected, targets)


if __name__ == '__main__':
    raise SystemExit(main())
