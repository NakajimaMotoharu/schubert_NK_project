"""One ordinary owned HTTP failure reproduction plus existing guards; no actual service/VM."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names

ROOT = engine.ROOT
OLD = 'acb5fe9c375ede57f5d15fc5fc392f2197c910d4'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementStopTest.java'


def inventory():
    cases = {m: set(v) for m, v in engine.CASES.items()}
    cases['api'].update(('api.bootstrap.ApiManagementServerTest', 'api.bootstrap.ApiManagementStopTest'))
    counts = {engine.PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.', '/')+'.java')))
              for m, names in cases.items() for c in names}
    if (sum(counts.values()), len(counts)) != (20, 9):
        raise ValueError('one new stop failure case/old seven management/twelve guards')
    return cases, counts


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed red snapshot first')
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != {TEST}:
        raise ValueError('all Main/oracles unchanged;one independent new failure fixture only')
    if subprocess.check_output(['git', 'diff', OLD, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current unchanged')
    cases, counts = inventory()
    scope = {**vars(engine), 'SLOT': 'pg6128-api-management-stop-red-v1',
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'api': ['api/bootstrap/ApiManagementServer']},
             'test_names': source_test_names}
    exec(compile(base_runner(20, 9, target_count=1), '<ordinary failure reproduction>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
