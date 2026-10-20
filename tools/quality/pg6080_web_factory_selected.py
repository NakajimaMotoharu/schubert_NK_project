"""SSC311 ordinary Web module regression and other-module guards; no deployed runtime."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
BASELINE = 'fa8580ce15a0292624cac2a12228abf1bcc79d1c'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBrokerFactoryOwnershipTest.java'


def inventory():
    cases = {k: set(v) for k, v in engine.CASES.items()}
    root = ROOT/'src/schubert-nk-web/src/test/java'
    cases['web'] = {p.relative_to(root).as_posix()[:-5].replace('/', '.').removeprefix(engine.PACKAGE)
                    for p in root.glob('**/*Test.java')}
    counts = {engine.PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/
              ((engine.PACKAGE+c).replace('.', '/')+'.java'))) for m, names in cases.items() for c in names}
    if (sum(counts.values()), len(counts)) != (925, 150):
        raise ValueError('917 original Web cases and eight guards,150 suites')
    return cases, counts


def runner_source():
    raw = base_runner(925, 150, target_count=1)
    changes = {
        'done=done  # partial coverage is reported,not invented or excluded': 'done=done and target100',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS'}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit Web selection/coverage/Node environment binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<ordinary Web factory ownership regression>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/Test/operator before PT')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', BASELINE, 'HEAD', '--', 'src'],
                                        cwd=ROOT, text=True).splitlines())
    if changed != {MAIN, TEST}:
        raise ValueError('only one provider Main and independent new factory Test')
    if subprocess.check_output(['git', 'diff', BASELINE, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw',
                                 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('unchanged build/static/Current gates')
    cases, counts = inventory()
    scope = {**vars(engine), 'SLOT': 'pg6080-web-factory-selected-v1', 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'web': ['web/messaging/WebBrokerContexts']},
             'test_names': source_test_names}
    exec(compile(runner_source(), '<normal finite Web925>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
