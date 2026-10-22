"""Reproduce/repair constructor cleanup only for newly owned disposable DB fixtures."""
import argparse
import json
import subprocess
import finite_selected_profile as profile
import test_support_profile as support
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT, W, BASE, sha

OLD = '94bc77764565d62985592a7e5b92e9206a2d8f4f'
FIXTURES = {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchDatabaseFixture.java',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/logging/ApiLogDatabaseFixture.java'}
TESTS = {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchFixtureOwnershipTest.java',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/logging/ApiLogFixtureOwnershipTest.java'}
SLOTS = {'red-bootstrap': 'pg6922-db-fixture-red-bootstrap-v1', 'red-batch': 'pg6922-db-fixture-red-batch-v1', 'green': 'pg6924-db-fixture-green-v1'}
RED_QSHA = '97db1cbbeefa2a43961686b891d15b82fc34579ceb431f93f9aa2f8b8267693d'
GREEN_EXPECTED = (21, 10)


def inventory(mode):
    extra = {'bootstrap': {'api.logging.ApiLogFixtureOwnershipTest'}} if mode == 'red-bootstrap' else {'batch': {'batch.repository.BatchFixtureOwnershipTest'}}
    if mode == 'green':
        extra = {'bootstrap': {'api.logging.ApiLogFixtureOwnershipTest'}, 'batch': {'batch.repository.BatchFixtureOwnershipTest'}, 'web': {'web.logging.WebLogDatabaseFixtureTest'}}
    return profile.inventory(extra, GREEN_EXPECTED if mode == 'green' else (15, 8))


def guard(source):
    changes = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changes) != FIXTURES | TESTS or len(changes) != 4:
        raise ValueError('only two declared test fixtures and two new Tests, all Main/old assertions fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/quality/Current fixed')


def green_guard(source):
    guard(source)
    qp = BASE / 'PG6926-db-fixture-red-original-v1/manifest.json'
    if RED_QSHA is None or sha(qp) != RED_QSHA:
        raise ValueError('freeze both genuine SQL failure/owned cleanup originals first')
    red = json.loads(qp.read_bytes())
    if not (red['readerActualExit'] == 0 and red['fixtureCounterexamples'] == 2):
        raise ValueError('both separate red module originals')
    if subprocess.check_output(['git', 'diff', red['source'], source, '--', *sorted(TESTS)], cwd=ROOT):
        raise ValueError('all independent new oracle bytes fixed since both red cases')


def read_green():
    run = W / SLOTS['green']
    source = json.loads((run / 'begin.safe.json').read_bytes())['source']
    green_guard(source)
    cases, _ = inventory('green')
    return prior.qualification_definition()(source, run, cases, GREEN_EXPECTED, set(),
      BASE / 'PG6918-observation-values-original-v1/manifest.json', '32118884012095e87885c0246f083a27193f2d56394842e8459eed4d770145f4',
      W / 'pg6918-observation-values-original-v1/manifest.safe.json', W / 'pg6918-observation-values-original-v1/findings.safe.json',
      'pg6928-db-fixture-green-original-v1', 'PG6928-db-fixture-green-original-v1', expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=(*SLOTS, 'read-green'))
    mode = parser.parse_args().action
    if mode == 'read-green':
        return read_green()
    cases, counts = inventory(mode)
    return support.execute(SLOTS[mode], green_guard if mode == 'green' else guard, cases, counts, GREEN_EXPECTED if mode == 'green' else (15, 8))


if __name__ == '__main__':
    main()
