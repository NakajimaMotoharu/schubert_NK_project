"""Normal API+Web regressions after four JMS ownership edits; no deployed runtime or VM actions."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
BASELINE = 'c4d0242abe53fa7916451ac22caffcdfc13d82b6'
PACKAGE = engine.PACKAGE
MAIN = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/QuestionWorkConsumers.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/ApiMessagingRuntime.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java'}
TESTS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/QuestionWorkConsumersTest.java',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumersTest.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumersTest.java'}


def inventory():
    cases = {k: set(v) for k, v in engine.CASES.items()}
    for module in ('api', 'web'):
        root = ROOT/('src/schubert-nk-'+module+'/src/test/java')
        cases[module] = {p.relative_to(root).as_posix()[:-5].replace('/', '.').removeprefix(PACKAGE) for p in root.glob('**/*Test.java')}
    counts = {PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((PACKAGE+c).replace('.', '/')+'.java'))) for m, names in cases.items() for c in names}
    return cases, counts


def runner_source(total, suites):
    raw = base_runner(total, suites, target_count=4)
    replacements = {
        'done=done  # partial coverage is reported,not invented or excluded': 'done=done and target100',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS'}
    for old, new in replacements.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit full module selection/target gate/Node environment binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<ordinary current JMS ownership regressions>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/Test/operator before PT')
    if set(subprocess.check_output(['git', 'diff', '--name-only', BASELINE, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != MAIN | TESTS:
        raise ValueError('exact four Main and three new public acquisition Tests only')
    if subprocess.check_output(['git', 'diff', BASELINE, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('unchanged build/static/Current gates')
    cases, counts = inventory()
    targets = {'api': ['api/messaging/inbound/'+n for n in ('QuestionWorkConsumers', 'WebLogConsumers', 'ApiMessagingRuntime')],
               'web': ['web/messaging/ArtemisReplyConsumers']}
    scope = {**vars(engine), 'SLOT': 'pg6074-jms-owner-selected-v1', 'NODE_PATH': node_environment(),
        'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': source_test_names}
    exec(compile(runner_source(sum(counts.values()), len(counts)), '<normal modules and guards>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
