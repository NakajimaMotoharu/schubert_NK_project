"""New deterministic self-TempDir NIO collision; no actual startup authority or recovery."""
import json
import subprocess
import pg6438_morning_diagnostic_red as prior

ROOT, W, BASE, sha = prior.ROOT, prior.W, prior.BASE, prior.sha
OLD = 'bbbc3f7f13b6858535515dc495ad53839683fb24'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupStartIntentCollisionTest.java'
SLOT = 'pg6466-nio-collision-selected-v1'


def inventory():
    cases = {m: set(v) for m, v in prior.prior.engine.CASES.items()}
    cases['batch'].add('batch.file.BackupStartIntentCollisionTest')
    counts = {prior.prior.engine.PACKAGE+name: len(prior.prior.source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/((prior.prior.engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (13, 8):
        raise ValueError('baseline12 plus one deterministic ordinary Test; repeated class not selected')
    return cases, counts


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one new Test only; every Main and existing oracle unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates and Current unchanged')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/operator first')
    import pg6456_current4056_trace as genuine
    genuine.read_qualified()
    guard_source('HEAD'); cases, counts = inventory()
    raw = prior.prior.runner_source(13, 8, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned ordinary Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(prior.prior.engine), 'SLOT': SLOT, 'NODE_PATH': prior.prior.node_environment(),
        'CASES': cases, 'COUNTS': counts, 'TARGETS': {'batch': ['batch/file/BackupStartIntentFiles']},
        'test_names': prior.prior.source_test_names}
    exec(compile(raw, '<self TempDir NIO deterministic collision13>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
