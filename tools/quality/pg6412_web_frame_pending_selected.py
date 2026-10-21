"""Test-only supplementary exceptional finally path; preserve fixed PG and original red oracle."""
import json
import subprocess
import pg6398_web_frame_green as prior

ROOT, W, BASE, sha = prior.ROOT, prior.W, prior.BASE, prior.sha
OLD = 'd319d68feeb241203a67e686dd03317782a04b77'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimePendingFailureRetentionTest.java'


def inventory():
    cases, _ = prior.inventory()
    cases['web'].add('web.bootstrap.WebRuntimePendingFailureRetentionTest')
    counts = {prior.red.engine.PACKAGE+name: len(prior.red.source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/((prior.red.engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (26, 12):
        raise ValueError('original25 declarations plus one pending-failure Test, not three cases as extra PT')
    return cases, counts


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one supplementary Test only; original PG/red/green oracle bytes unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates/Current unchanged')


def prior25():
    qp = BASE/'PG6400-web-frame-qualification-v1/manifest.json'; q = json.loads(qp.read_bytes())
    if not (sha(qp) == '59792d63765ca0713feebe147b225a82e3319f72984218d6940b43e198288ca3'
            and q['source'] == OLD and q['actualExit'] == 0 and (q['tests'], q['suites'], q['physicalMain']) == (25, 11, 1667)):
        raise ValueError('original25/all8511667 qualified, never replay for missing results')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed one supplementary Test/operator first')
    prior25(); guard_source('HEAD'); cases, counts = inventory()
    raw = prior.red.runner_source(26, 12, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(prior.red.engine), 'SLOT': 'pg6412-web-frame-pending-selected-v1', 'NODE_PATH': prior.red.node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': {'web': ['web/bootstrap/WebRuntimeExecution']},
             'test_names': prior.red.source_test_names}
    exec(compile(raw, '<26 independent normal and exceptional finally paths>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
