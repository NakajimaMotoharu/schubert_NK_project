"""Preserve observed EOF warnings as NOT_PASS; no Product quality waiver or replay."""
import hashlib
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE / 'PG17175-quality-save-eof-audit-v1'
OLD = data.BASE / 'PG17174-morning-launch-owner-public-save-v1'
PIN = '327396dc672be0f3b9ac31e66ecaa3b59b8cc38309ba65540758f4f32efd7610'
EXPECTED = {'documents/400_PGPT/450_品質/3342_MorningLaunchOwner原3仕様.md',
            'tools/quality/architecture/MorningLaunchOwnerThreeCurrentJunitLauncher.java',
            *('tools/quality/' + n for n in ('pg17160_morning_launch_owner_three_pt.py',
              'pg17162_morning_launch_owner_three_post.py', 'pg17164_morning_launch_owner_three_independent.py',
              'pg17166_current2609_morning_launch_owner_registry.py', 'pg17168_current2609_morning_launch_owner_registry_post.py',
              'pg17170_current2609_morning_launch_owner_wbs.py', 'pg17172_current2609_morning_launch_owner_wbs_post.py'))}


def assess(code, stdout, expected=EXPECTED):
    lines = stdout.splitlines()
    assert type(code) is int and code == 2 and len(lines) == 9
    found = set()
    for line in lines:
        path, number, message = line.rsplit(':', 2)
        assert number.strip().isdigit() and message == ' new blank line at EOF.'
        assert path in expected and path not in found
        found.add(path)
    assert found == expected


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    old = data.read_checked(OLD / 'manifest.json', PIN)
    assert old['actualExit'] == 0 and not old['findings']
    known = {v['path']: v['sha256'] for v in old['files']}
    assert EXPECTED <= known.keys()
    for path, pin in known.items():
        assert hashlib.sha256((data.ROOT / path).read_bytes()).hexdigest() == pin
    proc = subprocess.run(['git', '-c', 'core.quotepath=false', 'diff', '--cached', '--check'], cwd=data.ROOT,
                          capture_output=True, text=True, check=False)
    assert not proc.stderr
    assess(proc.returncode, proc.stdout)
    for path in EXPECTED:
        assert (data.ROOT / path).read_bytes().endswith(b'\n\n')
    negatives = [(0, proc.stdout), (2, proc.stdout.replace('new blank line at EOF.', 'trailing whitespace.', 1)),
                 (2, proc.stdout.splitlines()[0] + '\n'), (2, proc.stdout + proc.stdout.splitlines()[0] + '\n'),
                 (2, proc.stdout.replace('tools/quality/', 'src/', 1))]
    for code, output in negatives:
        try:
            assess(code, output)
        except AssertionError:
            pass
        else:
            raise ValueError('unrecognized whitespace accepted')
    inputs = ('', 'x', 'x\n', 'x\n\n')
    assert [v.rstrip('\n') + '\n' for v in inputs] == ['\n', 'x\n', 'x\n', 'x\n']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation,
        source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c', oldPublicSaveSha256=PIN,
        preservedFileHashes=known, gitCheckExit=proc.returncode, gitCheckStdout=proc.stdout,
        gitCheckStatus='NOT_PASS_NINE_EOF_ONLY_WARNINGS_PRESERVED_FOR_PROVENANCE',
        retainedWarningPaths=sorted(EXPECTED), negativeMetadataVectors=len(negatives), generatorBoundaryVectors=4,
        executedBytesChanged=False, gitWhitespaceConfigurationChanged=False, productionQualityConditionsChanged=False,
        commitPushMustBeSeparate=True, productTestsExecuted=0, newAccepted=0, formalUpdated=False,
        wholeF03Accepted=False, whole451Accepted=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
