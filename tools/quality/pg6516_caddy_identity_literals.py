"""Pure injected NSS record vectors; no real query/process or authority operations."""
import json
import subprocess
import pg5732_enum48_selected as engine
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
from pg6052_expiry_combined_selected import runner_source
from pg6470_web_owned_component_selected import compile_first

OLD = 'a03b6153469f3478ed3b40d2c82e3f89c4d221ab'
TEST = 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedCaddyIdentityTest.java'
SLOT = 'pg6516-caddy-identity-literals-v1'
Q = BASE/'PG6514-finite-policy-qualification-v1/manifest.json'
QSHA = '2664499fdf336a41910917a9392091abc86bcc7ba4f2f081de0de7553c58db5f'


def inventory():
    cases = {module: set(names) for module, names in engine.CASES.items()}
    cases['bootstrap'].add('bootstrap.FixedCaddyIdentityTest')
    counts = {engine.PACKAGE+name: len(source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/
        ((engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (15, 8):
        raise ValueError('unchanged twelve guards plus three literal contract Tests')
    return cases, counts


def guard_source(source):
    if sha(Q) != QSHA:
        raise ValueError('immutable original20 qualification required')
    q = json.loads(Q.read_bytes())
    if not (q['source'] == OLD and q['actualExit'] == 0 and not q['changedPhysical']
            and (q['tests'], q['suites'], q['sourceFiles'], q['physicalMain']) == (20, 8, 851, 1667)):
        raise ValueError('same-source original20 all-Main invariant')
    changed = subprocess.check_output(
        ['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if changed != [TEST]:
        raise ValueError('only independent literal Test; every Main and prior Test unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn',
                               'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates and Current unchanged')


def selected_runner():
    raw = runner_source(15, 8, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('single pinned Node environment')
    return compile_first(raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1))


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/operator first')
    guard_source('HEAD')
    cases, counts = inventory()
    scope = {**vars(engine), 'SLOT': SLOT, 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts,
             'TARGETS': {'bootstrap': ['bootstrap/FixedServiceIdentity']},
             'test_names': source_test_names}
    exec(compile(selected_runner(), '<pure fixed Caddy fifteen>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
