"""SSC327 ordinary self-owned DB/JMS/HTTP, not real Root/VM/permit/native qualification."""
import json
import subprocess
import pg6466_nio_collision_selected as prior

ROOT, W, BASE, sha = prior.ROOT, prior.W, prior.BASE, prior.sha
OLD = '7059b1e1f4403078bb6bbc7d8c8371e68aeaff2f'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntimeOwnedComponentTest.java'
SLOT = 'pg6470-web-owned-component-v1'
COMPILE_BEFORE_PT = False


def compile_first(raw):
    before = "commands=[base+['spotless:check'],base+['-Dtest='"
    after = "commands=[base+['spotless:check'],base+['-DskipTests','test-compile'],base+['-Dtest='"
    if raw.count(before) != 1 or raw.count('exits==[0,0]') != 1:
        raise ValueError('explicit three-phase profile; no test skip in execution phase')
    return raw.replace(before, after, 1).replace('exits==[0,0]', 'exits==[0,0,0]', 1)


def inventory():
    cases, _ = prior.inventory()
    cases['web'].update('web.bootstrap.'+name for name in (
        'WebNativeRuntimePartialTest', 'WebRuntimeRemainderTest', 'WebNativeRuntimeOwnedComponentTest'))
    counts = {prior.prior.prior.engine.PACKAGE+name: len(prior.prior.prior.source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/((prior.prior.prior.engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (27, 11):
        raise ValueError('own component7/partial3/remainder4 plus unchanged13, not matrix invocation counts')
    return cases, counts


def guard_source(source):
    qpath = BASE/'PG6468-nio-collision-qualification-v1/manifest.json'
    q = json.loads(qpath.read_bytes())
    if sha(qpath) != '6c5e59a7af3d9f88b8b8af6cc8f85346be7d17e1a9e2ab4c89957e2efa432c6e' or q['source'] != OLD or q['actualExit'] != 0 or q['changedPhysical']:
        raise ValueError('prior original13 all-Main/Jar unchanged qualification first')
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != {MAIN, TEST}:
        raise ValueError('one localized Web PG and one independent Test only')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates and Current unchanged')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed PG/Test/operator first')
    guard_source('HEAD'); cases, counts = inventory(); engine = prior.prior.prior.engine
    raw = prior.prior.prior.runner_source(27, 11, target_count=2)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    if COMPILE_BEFORE_PT:
        raw = compile_first(raw)
    scope = {**vars(engine), 'SLOT': SLOT, 'NODE_PATH': prior.prior.prior.node_environment(),
        'CASES': cases, 'COUNTS': counts,
        'TARGETS': {'web': ['web/bootstrap/WebNativeRuntime'], 'batch': ['batch/file/BackupStartIntentFiles']},
        'test_names': prior.prior.prior.source_test_names}
    exec(compile(raw, '<own Web component27>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
