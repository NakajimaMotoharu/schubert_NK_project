"""SSC314 full API/Web ordinary self-owned PT; six static modules, no actual VM/current."""
import subprocess
import pg5732_enum48_selected as engine
from pg6074_jms_owner_selected import inventory
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
BASELINE = 'ca0383ac0729065fe03d4cd4b1303c9afa7e4b21'
PREFIX = 'src/schubert-nk-api/src/'
MAIN = {PREFIX+'main/java/dev/codex/schubert/nk/api/'+p+'.java' for p in (
    'messaging/inbound/SyncRequestConsumers', 'messaging/inbound/WebLogConsumers',
    'messaging/inbound/QuestionWorkConsumers', 'messaging/inbound/ApiMessagingRuntime',
    'messaging/config/ApiBrokerContexts')}
TESTS = {PREFIX+'test/java/dev/codex/schubert/nk/api/'+p+'.java' for p in (
    'messaging/inbound/ApiConsumerCloseOwnershipTest', 'messaging/inbound/ApiMessagingRuntimeTest',
    'messaging/config/ApiBrokerContextsTest', 'bootstrap/ApiManagementStopTest')}
TARGETS = {'api': ['api/messaging/inbound/'+n for n in (
    'SyncRequestConsumers', 'WebLogConsumers', 'QuestionWorkConsumers', 'ApiMessagingRuntime')]
    + ['api/messaging/config/ApiBrokerContexts', 'api/bootstrap/ApiManagementServer']}


def runner_source():
    raw = base_runner(1950, 320, target_count=6)
    replacements = {
        'done=done  # partial coverage is reported,not invented or excluded': 'done=done and target100',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS'}
    for before, after in replacements.items():
        if raw.count(before) != 1:
            raise ValueError('one exact ordinary selection/coverage/Node environment binding')
        raw = raw.replace(before, after, 1)
    compile(raw, '<API JMS close ordinary PT>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/Test/operator first')
    if set(subprocess.check_output(['git', 'diff', '--name-only', BASELINE, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != MAIN | TESTS:
        raise ValueError('five exact Main/four Test changes including owned fixture cleanup')
    if subprocess.check_output(['git', 'diff', BASELINE, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current/oracles unchanged outside documented close oracle')
    cases, counts = inventory()
    if (sum(counts.values()), len(counts)) != (1950, 320):
        raise ValueError('all current API/Web plus guards; seven additional independent Tests')
    scope = {**vars(engine), 'SLOT': 'pg6140-api-jms-close-selected-v1', 'NODE_PATH': node_environment(),
        'CASES': cases, 'COUNTS': counts, 'TARGETS': TARGETS, 'test_names': source_test_names}
    exec(compile(runner_source(), '<ordinary API/Web self-owned tests>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
