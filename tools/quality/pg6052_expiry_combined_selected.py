"""PTPRE032: new-only ordinary pure JDBC red/green; no current/VM/cohort or service actions."""
import argparse
import inspect
import subprocess
import pg5732_enum48_selected as engine
from pg5966_api_sql_selected import source_test_names

ROOT = engine.ROOT
MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditResourceFailureTest.java'
OLD_TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepositoryTest.java'
BASE = '8c869d7cea21d587b859b3e72e3516d9d2deb5c8'


def runner_source(total, suites):
    raw = inspect.getsource(engine.main)
    changes = {
        "count=3 if module=='protocol'else 4 if module=='web'else 1": 'count=COUNTS[name]',
        'sum(map(len,expected.values()))!=12 or len(expected)!=7': f'sum(map(len,expected.values()))!={total} or len(expected)!={suites}',
        "'expectedTests':12": f"'expectedTests':{total}",
        "method=case.get('name','').removesuffix('()')": "method=case.get('name','').split('(',1)[0]",
        'len(physical)==1664': 'len(physical)==1667',
        'done=done and target100': 'done=done  # partial coverage is reported,not invented or excluded',
        "'actualExit':next((v for v in exits if v),0)": "'actualExit':0 if done else 1,'mavenActualExit':next((v for v in exits if v),0)",
    }
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit normal finite selected-run binding: ' + old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<pure JDBC finite selected profile>', 'exec')
    return raw


def inventory(phase='red'):
    cases = {m: set(v) for m, v in engine.CASES.items()}
    cases['batch'].add('batch.repository.ExpiryAuditResourceFailureTest')
    if phase == 'green':
        cases['batch'].update('batch.repository.'+name for name in (
            'ExpiryAuditRepositoryTest', 'ExpirySuccessfulScopeTest',
            'MorningExpiryObservationInvariantTest', 'MorningExpirySessionTest',
            'MorningDatabaseAccessContractTest', 'MorningDatabaseSessionTest'))
        cases['batch'].update(('batch.file.CleanupExpiryExecutionTest', 'batch.file.RetainedExpiryAuditTest'))
    counts = {engine.PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.', '/')+'.java'))) for m, cs in cases.items() for c in cs}
    return cases, counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('red', 'green'))
    args = parser.parse_args()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/source/operator first')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', BASE, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines())
    if changed != ({TEST} if args.phase == 'red' else {TEST, MAIN, OLD_TEST}):
        raise ValueError('only focused Test on old Main(red),localized read+Test(green)')
    if subprocess.check_output(['git', 'diff', BASE, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('unchanged build/static/Current gates')
    cases, counts = inventory(args.phase)
    if args.phase == 'red' and (sum(counts.values()), len(counts)) != (13, 8):
        raise ValueError('one independent counterexample plus twelve unchanged guards')
    targets = {'batch': ['batch/repository/ExpiryAuditRepository']}
    scope = {**vars(engine), 'SLOT': 'pg6052-expiry-combined-'+args.phase+'-v1',
             'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': source_test_names}
    exec(compile(runner_source(sum(counts.values()), len(counts)), '<approved pure proxy PT>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
