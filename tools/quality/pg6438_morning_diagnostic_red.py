"""PT_DEFAULT pure injected clock/sink; one preserved Test-file change, no Root/Unit invocation."""
import json
import subprocess
import pg6396_web_frame_red as prior

ROOT, W, BASE, sha = prior.ROOT, prior.W, prior.BASE, prior.sha
OLD = '669ad5fd83f67ad031b2c1734d7fc5716599d35d'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCompletionRetirementTest.java'
SLOT = 'pg6438-morning-diagnostic-red-v1'


def inventory():
    cases = {m: set(v) for m, v in prior.engine.CASES.items()}
    cases['batch'].add('batch.file.MorningCompletionRetirementTest')
    counts = {prior.engine.PACKAGE+name: len(prior.source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/((prior.engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (18, 8):
        raise ValueError('six actual Completion Test methods plus baseline12; matrix not extra PT')
    return cases, counts


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one extended independent Test file only; every Main fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates and Current unchanged')


def original4054():
    p = BASE/'PG6408-current4054-cases/qualification.json'; q = json.loads(p.read_bytes())
    r = json.loads((W/'pg6410-original4054-artifacts-v1/manifest.safe.json').read_bytes())
    if not (sha(p) == '2fe8efc5bc8ad1c60487a1366ba80c159fe8c61cf937fd2509b8d4298591b0a7'
            and q['productionSource'] == r['source'] == OLD and q['actualExit'] == r['actualExit'] == 0
            and (q['tests'], q['suites'], q['mainClasses']) == (4054, 610, 1667)
            and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
            and r['wholeReplayed'] is False and r['publicQualificationSha256'] == sha(p)):
        raise ValueError('genuine original4054 complete before new Test/source')


def definitions():
    cases, counts = inventory(); raw = prior.runner_source(18, 8, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned ordinary Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(prior.engine), 'SLOT': SLOT, 'NODE_PATH': prior.node_environment(),
        'CASES': cases, 'COUNTS': counts,
        'TARGETS': {'batch': ['batch/file/MorningStartupLaunchOwner$CompletionProgress']},
        'test_names': prior.source_test_names}
    exec(compile(raw, '<pure Morning progress diagnostic counterexample>', 'exec'), scope)
    return scope


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/operator first')
    original4054(); guard_source('HEAD')
    return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
