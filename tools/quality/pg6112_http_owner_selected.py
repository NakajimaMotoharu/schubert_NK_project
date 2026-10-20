"""SSC312 ordinary API/Web finite fixture tests; no deployed VM/current operations."""
import subprocess
import pg5732_enum48_selected as engine
from pg6074_jms_owner_selected import inventory
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
OLD = '59960d19c226fd524bb608a34299d7616433ae50'
OWNERS = {'api': ['api/bootstrap/ApiManagementServer'],
          'web': ['web/bootstrap/WebManagementServer', 'web/bootstrap/WebHttpServer']}
PATHS = {f'src/schubert-nk-{module}/src/{tree}/java/dev/codex/schubert/nk/{name}{suffix}.java'
         for module, names in OWNERS.items() for name in names
         for tree, suffix in [('main', ''), ('test', 'Test')]}


def runner_source():
    raw = base_runner(1939, 318, target_count=3)
    replacements = {
        'done=done  # partial coverage is reported,not invented or excluded': 'done=done and target100',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS'}
    for old, new in replacements.items():
        if raw.count(old) != 1:
            raise ValueError('exact target counter and pinned Node binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<ordinary HTTP owner regressions>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/Test/operator first')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines())
    if changed != PATHS:
        raise ValueError('three HTTP owners and three independent tests only')
    if subprocess.check_output(['git', 'diff', OLD, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('unchanged build/static/oracles/Current')
    cases, counts = inventory()
    if (sum(counts.values()), len(counts)) != (1939, 318):
        raise ValueError('original full API/Web plus three new tests and guards')
    scope = {**vars(engine), 'SLOT': 'pg6112-http-owner-selected-v1', 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': OWNERS, 'test_names': source_test_names}
    exec(compile(runner_source(), '<ordinary HTTP1939>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
