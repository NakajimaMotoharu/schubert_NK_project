"""Related54 on two corrected Main only; all independent red tests/oracles remain fixed."""
import json
import subprocess
import xml.etree.ElementTree as ET
import pg6360_web_startup_red as red
from pg5940_private_lock_compile import W

ROOT = red.ROOT
OLD = 'db7782a334a3db35598ede4f765d71e52e3677cb'
MAIN = {
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java',
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntime.java'
}


def inventory():
    cases, _ = red.inventory()
    cases['web'].update(('web.bootstrap.WebLogApplicationRuntimeTest', 'web.logging.WebLogReplayWorkerTest',
                         'web.messaging.ArtemisReplyConsumersTest', 'web.bootstrap.WebRuntimeExecutionTest'))
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    base = red.previous.previous.prior
    counts = {base.engine.PACKAGE+n: len(base.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((base.engine.PACKAGE+n).replace('.', '/')+'.java')))
              for m, names in cases.items() for n in names}
    if (sum(counts.values()), len(counts)) != (54, 15):
        raise ValueError('actual54 independently declared methods/15 suites, not prior18 arithmetic PASS')
    return cases, counts


def reproduced():
    run = W/'pg6360-web-startup-red-v1'; value = json.loads((run/'manifest.safe.json').read_bytes())
    path = run/'source/src/schubert-nk-web/target/surefire-reports/TEST-dev.codex.schubert.nk.web.bootstrap.WebStartupRetentionTest.xml'
    root = ET.parse(path).getroot()
    failures = {r.get('name') for r in root.findall('testcase') if r.find('failure') is not None}
    if not (value['source'] == OLD and value['actualExit'] == value['mavenActualExit'] == 1 and value['sourceFixed']
            and (value['tests'], value['suites']) == (18, 8)
            and [int(root.get(k)) for k in ('tests', 'failures', 'errors', 'skipped')] == [2, 2, 0, 0]
            and failures == {'start324001NormalOrderNullableWorkerAndNullBoundary',
                             'start324002UnknownCleanupRetainsDummyOwnersAcrossInterruptInOwnedJvm'}):
        raise ValueError('genuine original red XML/terminal before PG, no replay for results')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed two Main/operator before selected run')
    reproduced()
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()) != MAIN:
        raise ValueError('exact two Main only; all original red Test/oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates/Current unchanged')
    raw = red.runner()
    for before, after in (('runner_source(20,10,target_count=16)', 'runner_source(54,15,target_count=16)'),
                          ('pg6360-web-startup-red-v1', 'pg6364-web-startup-selected-v1'),
                          ('def run_red():', 'def run_green():')):
        if raw.count(before) != 1:
            raise ValueError('explicit related54 binding '+before)
        raw = raw.replace(before, after, 1)
    scope = {**vars(red.previous.previous.prior), 'inventory': inventory}
    exec(compile(raw, '<related54 startup ownership correction>', 'exec'), scope)
    return scope['run_green']()


if __name__ == '__main__':
    raise SystemExit(main())
