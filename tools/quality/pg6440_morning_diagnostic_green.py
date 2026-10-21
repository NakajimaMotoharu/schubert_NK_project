"""Same independent oracle plus normal owner contract, only after genuine red is pinned."""
import json
import subprocess
import pg6438_morning_diagnostic_red as red

ROOT, W, BASE, sha = red.ROOT, red.W, red.BASE, red.sha
MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner.java'
RED_SOURCE = '6c066eb2b0b13e252e9646bca98594f16ab87002'
RED_MANIFEST_SHA = 'ae374b34203709abf3d5cad51447c4986bd53c43bfafe85044ba7ebe7d92e897'
RED_COUNTS = (18, 8)
FAILED = ['dev.codex.schubert.nk.batch.file.MorningCompletionRetirementTest',
          'completion326001FailureDiagnosticCannotThrowBeforeOwnerRetention']


def inventory():
    cases, _ = red.inventory()
    cases['batch'].update(('batch.file.MorningStartupLaunchOwnerTest', 'batch.file.MorningStartupLaunchOwnerAdmissionTest'))
    counts = {red.prior.engine.PACKAGE+name: len(red.prior.source_test_names(
        ROOT/('src/schubert-nk-'+module+'/src/test/java')/((red.prior.engine.PACKAGE+name).replace('.', '/')+'.java')))
        for module, names in cases.items() for name in names}
    if (sum(counts.values()), len(counts)) != (23, 10):
        raise ValueError('actual18 plus existing3 owner/2admission, not fixture counts as PT')
    return cases, counts


def guard_source(source):
    if RED_SOURCE is None or RED_MANIFEST_SHA is None or RED_COUNTS is None:
        raise ValueError('pin genuine counterexample before Production change/green')
    p = W/red.SLOT/'manifest.safe.json'; m = json.loads(p.read_bytes())
    if not (sha(p) == RED_MANIFEST_SHA and m['source'] == RED_SOURCE and m['actualExit'] == m['mavenActualExit'] == 1
            and m['phaseExits'] == [0, 1] and m['sourceFixed']
            and (m['tests'], m['suites']) == RED_COUNTS and m['failedOrSkipped'] == [FAILED]):
        raise ValueError('same original genuine failed independent method, never failed result normalized')
    red.guard_source(RED_SOURCE)
    if subprocess.check_output(['git', 'diff', '--name-only', RED_SOURCE, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [MAIN]:
        raise ValueError('one localized Main only; all original Test bytes preserved')
    if subprocess.check_output(['git', 'diff', RED_SOURCE, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates/Current unchanged')


def definitions():
    cases, counts = inventory(); raw = red.prior.runner_source(23, 10, target_count=1)
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned ordinary Node environment')
    raw = raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1)
    scope = {**vars(red.prior.engine), 'SLOT': 'pg6440-morning-diagnostic-green-v1', 'NODE_PATH': red.prior.node_environment(),
        'CASES': cases, 'COUNTS': counts,
        'TARGETS': {'batch': ['batch/file/MorningStartupLaunchOwner$CompletionProgress']},
        'test_names': red.prior.source_test_names}
    exec(compile(raw, '<same independent diagnostic oracle and normal owner contracts>', 'exec'), scope)
    return scope


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed one-Main PG first')
    guard_source('HEAD')
    return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
