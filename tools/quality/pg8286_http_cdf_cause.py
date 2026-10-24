"""BUG1696 cause from new own scalar fixture, no replay of failed PT or target operation."""
import json
import os
from pathlib import Path
import scoped_prometheus_host as run
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    raw = run.host.W / 'pg8284-http-cdf-lifetime-host-v1/manifest.safe.json'
    assert run.host.sha(raw) == '27bd965b2b2c9d78b14830284ebd6af0ed7b0da89da10a80f4d5f3fcc42c221c'
    original = json.loads(raw.read_text())
    assert original['actualExit'] == 1 and len(original['cases']) == 3 and all(c['result'] == 'NOT_PASS' for c in original['cases'])
    inputs = original['begin']['dependencyHashes']
    assert all(run.host.sha(Path(p)) == h for p, h in inputs.items())
    helper = run.host.ROOT / 'tools/quality/architecture/HttpCdfLifetimeDiagnostic.java'
    helper_sha = run.host.sha(helper)
    run.SLOT = run.host.W / 'pg8286-http-cdf-cause-v1'
    out = run.host.BASE / 'PG8286-http-cdf-cause-v1'
    run.SLOT.mkdir(exist_ok=False)
    classes = run.SLOT / 'fresh-diagnostic-classes'
    classes.mkdir()
    cp = os.pathsep.join([str(classes), *inputs])
    jdk = run.host.TC / 'jdk-25.0.4/bin'
    stages = [run.step('compile', [str(jdk / 'javac'), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', cp, '-d', str(classes), str(helper)])]
    assert stages[-1]['actualExit'] == 0
    stages.append(run.step('diagnostic', [str(jdk / 'java'), '-cp', cp, 'HttpCdfLifetimeDiagnostic']))
    assert stages[-1]['actualExit'] == 0
    observations = [json.loads(line.removeprefix('DIAG ')) for line in (run.SLOT / 'diagnostic.log').read_text().splitlines() if line.startswith('DIAG ')]
    assert len(observations) == 4 and {r['kind'] for r in observations} == {'HTTP_BEFORE', 'HTTP_AFTER', 'DB_EXACT', 'MQ_EXACT'}
    assert run.host.sha(helper) == helper_sha and all(run.host.sha(Path(p)) == h for p, h in inputs.items())
    verify(invocation)
    out.mkdir(exist_ok=False)
    value = dict(actualExit=0, source=original['source'], originalFailedRawSha256=run.host.sha(raw), invocation=invocation, helperSha256=helper_sha, stages=stages, observations=observations, productionPT=0, purpose='OWN_MEMORY_SCALAR_DIAGNOSIS_NOT_TEST_PASS', actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0)
    run.host.write(out / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, observations=observations, manifestSha256=run.host.sha(out / 'manifest.json'))))
