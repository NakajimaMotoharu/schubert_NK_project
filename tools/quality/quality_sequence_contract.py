"""Independent first/second failure gates; no Maven/VM/production work invoked."""
import pathlib
import subprocess


def main():
    for first, second, expected, output in ((17, 0, 17, ''), (0, 23, 23, 'SECOND\n'), (0, 0, 0, 'SECOND\n')):
        script = 'set -eu; result=0; ( sh -c "exit ' + str(first) + '" && { echo SECOND; sh -c "exit ' + str(second) + '"; } ) || result=$?; exit "$result"'
        p = subprocess.run(['bash', '-c', script], capture_output=True, text=True, timeout=5)
        assert p.returncode == expected and p.stdout == output and not p.stderr
    root = pathlib.Path('tools/quality/vm/050_s1')
    selected = (root / 'pg597_public_agent_driver_v1.sh').read_text()
    assert 'python3 -B tools/quality/qualified_nullable_check.py &&\n./mvnw ' in selected
    for name in ('pg585_access_pt_v1.sh', 'pg587_access_returns_v1.sh'):
        source = (root / name).read_text()
        body = source.split('task_result=0\n(\n', 1)[1].split(') > "$task_base/build.private.log"', 1)[0]
        assert body.count('./mvnw ') == 1 and 'python3' not in body
    print({'sequenceFixtures': 3, 'firstFailureSecondInvocations': 0, 'otherSingleCommandRunners': 2, 'actualExit': 0, 'productionPTCredit': 0})


if __name__ == '__main__':
    main()
