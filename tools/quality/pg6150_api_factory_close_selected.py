"""Combined SSC314/315 current API/Web regressions after coupled close/factory changes."""
import subprocess
import pg5732_enum48_selected as engine
from pg6074_jms_owner_selected import inventory
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
from pg6140_api_jms_close_selected import MAIN as STOP_MAIN, TESTS as STOP_TESTS, BASELINE

ROOT = engine.ROOT
MAIN = STOP_MAIN | {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ArtemisConnectionFactoryProvider.java'}
TESTS = STOP_TESTS | {'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/'+p+'.java' for p in (
    'inbound/QuestionWorkConsumersTest', 'inbound/SyncRequestConsumersTest', 'inbound/WebLogConsumersTest',
    'inbound/ApiConsumerRemainderTest', 'config/ApiFactoryOwnershipTest', 'config/ApiBrokerFactoryRemainderTest')}
TARGETS = {'api': ['api/messaging/inbound/'+n for n in (
    'SyncRequestConsumers', 'WebLogConsumers', 'QuestionWorkConsumers', 'ApiMessagingRuntime')]
    + ['api/messaging/config/'+n for n in ('ApiBrokerContexts', 'ArtemisConnectionFactoryProvider',
        'ArtemisConnectionFactoryProvider$ConsumerProfile')]+['api/bootstrap/ApiManagementServer']}


def runner_source():
    raw = base_runner(1955, 321, target_count=8)
    for before, after in {
        'done=done  # partial coverage is reported,not invented or excluded': 'done=done and target100',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS'}.items():
        if raw.count(before) != 1:
            raise ValueError('one current inventory/strict actual target/Node binding')
        raw = raw.replace(before, after, 1)
    compile(raw, '<combined ordinary API close/factory PT>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed fixed Main/Test/operator first')
    if set(subprocess.check_output(['git', 'diff', '--name-only', BASELINE, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != MAIN | TESTS:
        raise ValueError('exact six coupled Main/ten Test including eight old-oracle corrections')
    if subprocess.check_output(['git', 'diff', BASELINE, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current unchanged')
    cases, counts = inventory()
    if (sum(counts.values()), len(counts)) != (1955, 321):
        raise ValueError('all current API/Web plus guards, no arithmetic PASS aggregation')
    scope = {**vars(engine), 'SLOT': 'pg6150-api-factory-close-selected-v1', 'NODE_PATH': node_environment(),
        'CASES': cases, 'COUNTS': counts, 'TARGETS': TARGETS, 'test_names': source_test_names}
    exec(compile(runner_source(), '<ordinary current combined path>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
