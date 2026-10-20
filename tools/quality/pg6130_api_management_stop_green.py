"""SSC313 management component and guards; actual phase/lock/worker tests,no VM/current."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg6128_api_management_stop_red import OLD, TEST

ROOT = engine.ROOT
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java'


def inventory():
    cases = {m: set(v) for m, v in engine.CASES.items()}
    cases['api'].update(('api.bootstrap.ApiManagementServerTest', 'api.bootstrap.ApiManagementStopTest'))
    counts = {engine.PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.', '/')+'.java')))
              for m, names in cases.items() for c in names}
    if (sum(counts.values()), len(counts)) != (23, 9):
        raise ValueError('four independent stop Tests/old seven management/twelve guards')
    return cases, counts


def runner_source():
    raw = base_runner(23, 9, target_count=1)
    before = 'done=done  # partial coverage is reported,not invented or excluded'
    if raw.count(before) != 1:
        raise ValueError('one explicit target gate')
    raw = raw.replace(before, 'done=done and target100', 1)
    compile(raw, '<management stop green>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/Test/operator first')
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != {MAIN, TEST}:
        raise ValueError('one management Main/one new independent Test only')
    if subprocess.check_output(['git', 'diff', OLD, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current/oracles unchanged')
    cases, counts = inventory()
    scope = {**vars(engine), 'SLOT': 'pg6130-api-management-stop-green-v1',
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'api': ['api/bootstrap/ApiManagementServer']},
             'test_names': source_test_names}
    exec(compile(runner_source(), '<ordinary actual stop/lock/join>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
