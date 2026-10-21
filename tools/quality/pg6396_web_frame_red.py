"""New-only dummy Web borrowed-frame counterexample; wait for original4052 before Test install."""
import json
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
from pg5940_private_lock_compile import ROOT, W, BASE, sha

OLD = 'c34159083bfec296fd929ec9b2fbdbb80831c05c'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeExecutionRetentionTest.java'
DRAFT = ROOT/'tools/quality/fixtures/pg6396/WebRuntimeExecutionRetentionTest.java'
WHOLE_QUALIFICATION_SHA = '5b42051bf7ca435c44e3f7caa2fb0fca245faae9c32c3fda4b508ee40a4314b4'


def inventory(draft=False):
    cases = {m: set(v) for m, v in engine.CASES.items()}
    cases['web'].update(('web.bootstrap.WebRuntimeExecutionTest', 'web.bootstrap.WebRuntimeExecutionRetentionTest'))
    counts = {}
    for module, names in cases.items():
        for name in names:
            path = ROOT/('src/schubert-nk-'+module+'/src/test/java')/((engine.PACKAGE+name).replace('.', '/')+'.java')
            if draft and path == ROOT/TEST:
                path = DRAFT
            counts[engine.PACKAGE+name] = len(source_test_names(path))
    if (sum(counts.values()), len(counts)) != (15, 9):
        raise ValueError('baseline12 + existingExecution2 + one Test with9 child modes, not24 tests')
    return cases, counts


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one new Test only; all Main and prior oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing build/null/static/Current gates unchanged')


def original4052():
    path = BASE/'PG6386-current4052-cases/qualification.json'
    if WHOLE_QUALIFICATION_SHA is None or sha(path) != WHOLE_QUALIFICATION_SHA:
        raise ValueError('bind actual original4052 before changing its Main/Test source')
    q = json.loads(path.read_bytes())
    receipt = json.loads((W/'pg6388-original4052-artifacts-v1/manifest.safe.json').read_bytes())
    if not (q['productionSource'] == receipt['source'] == OLD and q['actualExit'] == receipt['actualExit'] == 0
            and (q['tests'], q['suites'], q['mainClasses']) == (4052, 608, 1667)
            and q['currentOriginalXmlQualified'] and q['returnedOriginalTerminalExact']
            and receipt['wholeReplayed'] is False and receipt['publicQualificationSha256'] == sha(path)):
        raise ValueError('genuine same original4052 terminal and independent all-artifact proof first')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/operator first')
    original4052(); guard_source('HEAD'); cases, counts = inventory()
    raw = runner_source(15, 9, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned ordinary Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(engine), 'SLOT': 'pg6396-web-frame-red-v1', 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'web': ['web/bootstrap/WebRuntimeExecution']},
             'test_names': source_test_names}
    exec(compile(raw, '<dummy Web borrowed-frame red15>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
