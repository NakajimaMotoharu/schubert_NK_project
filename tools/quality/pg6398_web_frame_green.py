"""Related25 after one borrowed-frame Main correction; never import failed red PASS."""
import json
import subprocess
import pg6396_web_frame_red as red

ROOT, W, BASE, sha = red.ROOT, red.W, red.BASE, red.sha
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeExecution.java'
RED_SOURCE = '46b0c4a4972c10e153b91cb4ae5dd637effbc02d'
RED_MANIFEST_SHA = '8d868c1ec153e416da93071170968a1b0628f805bb8230c6c984dd34df250ce1'


def inventory(draft=False):
    cases, _ = red.inventory(draft=draft)
    cases['web'].add('web.bootstrap.WebProcessLifetimeTest')
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    counts = {}
    for module, names in cases.items():
        for name in names:
            path = ROOT/('src/schubert-nk-'+module+'/src/test/java')/((red.engine.PACKAGE+name).replace('.', '/')+'.java')
            if draft and path == ROOT/red.TEST:
                path = red.DRAFT
            counts[red.engine.PACKAGE+name] = len(red.source_test_names(path))
    if (sum(counts.values()), len(counts)) != (25, 11):
        raise ValueError('actual baseline12/Execution2/new1/Life5/shared5 declarations')
    return cases, counts


def guard_source(source):
    if RED_SOURCE is None or RED_MANIFEST_SHA is None:
        raise ValueError('bind genuine red evidence before PG green')
    path = W/'pg6396-web-frame-red-v1/manifest.safe.json'
    m = json.loads(path.read_bytes())
    if not (sha(path) == RED_MANIFEST_SHA and m['source'] == RED_SOURCE
            and m['actualExit'] == m['mavenActualExit'] == 1 and m['sourceFixed']
            and m['phaseExits'] == [0, 1] and (m['tests'], m['suites']) == (13, 7)
            and m['failedOrSkipped'] == [['dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecutionRetentionTest',
                                        'exec325001UnknownCloseAndDiagnosticFailuresNeverUnwindOrRetry']]):
        raise ValueError('same original red terminal and source, no failed result normalization')
    red.guard_source(RED_SOURCE)
    if subprocess.check_output(['git', 'diff', '--name-only', RED_SOURCE, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [MAIN]:
        raise ValueError('one localized Main only; same independent red oracle and all other Test/Main fixed')
    if subprocess.check_output(['git', 'diff', RED_SOURCE, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates and Current unchanged')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed one-Main PG first')
    guard_source('HEAD'); cases, counts = inventory()
    raw = red.runner_source(25, 11, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(red.engine), 'SLOT': 'pg6398-web-frame-green-v1', 'NODE_PATH': red.node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'web': ['web/bootstrap/WebRuntimeExecution']},
             'test_names': red.source_test_names}
    exec(compile(raw, '<same oracle related25 borrowed-frame PG>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
