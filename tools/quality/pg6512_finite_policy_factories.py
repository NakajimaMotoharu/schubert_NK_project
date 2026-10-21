"""Finite own-JVM policies only; no actual Root, VM, recovery or authority operation."""
import json
import subprocess
import pg5732_enum48_selected as engine
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
from pg6052_expiry_combined_selected import runner_source
from pg6470_web_owned_component_selected import compile_first

OLD = 'e45cfd31c8d610922f4e9432cc1cf11fa9b48338'
TEST = 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java'
SLOT = 'pg6512-finite-policy-factories-v1'
Q = BASE/'PG6490-current4064-cases/qualification.json'
QSHA = 'c226dd9d40c491c44edf7a598aa9748ca90a58229b8849b8a6936cea136fb811'


def inventory():
    cases = {module: set(names) for module, names in engine.CASES.items()}
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    counts = {engine.PACKAGE+name: len(source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/
        ((engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (20, 8):
        raise ValueError('unchanged twelve guards plus eight real ordinary Test declarations')
    return cases, counts


def guard_source(source):
    if sha(Q) != QSHA:
        raise ValueError('immutable original whole qualification required')
    q = json.loads(Q.read_bytes())
    if not (q['productionSource'] == q['sourceSnapshot'] == OLD
            and q['actualExit'] == q['FESFlakyNotRun'] == q['staticSixModules'] == 0
            and q['returnedOriginalTerminalExact']
            and (q['tests'], q['suites'], q['mainClasses']) == (4064, 612, 1667)):
        raise ValueError('qualified Main/Test origin, not another-source success')
    changed = subprocess.check_output(
        ['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if changed != [TEST]:
        raise ValueError('only the three new independent Tests; every Main unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn',
                               'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates and Current unchanged')


def selected_runner():
    raw = runner_source(20, 8, target_count=1)
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
             'TARGETS': {'bootstrap': ['api/file/ServiceProcessResources']},
             'test_names': source_test_names}
    exec(compile(selected_runner(), '<finite policy twenty>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
