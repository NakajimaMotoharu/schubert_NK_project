"""Read saved exact public evidence and the source span of original PMD 327."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TARGET = 'dev/codex/schubert/nk/batch/platform/BackupUnitStartClient'
CODE = Path('src/schubert-nk-batch/src/main/java') / (TARGET + '.java')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    start = json.loads(next(D.glob('630_F03*')).read_bytes())['values']
    assert git('rev-parse', 'HEAD').decode().strip() == start['source']
    inputs = []
    for ref in start['oracleReferences']:
        data = Path(ref['path']).read_bytes()
        assert sha(data) == ref['sha256']
        inputs.append(json.loads(data))
    candidates, raw, physical, prior = inputs
    core = start['productionCoreMain']
    assert core == physical['sourceCore'] == prior['sourceCore']
    assert prior['findingId'] == 329 and prior['unclassifiedAfter'] == 32
    assert prior['applicableOpenInOriginal45'] == 13
    finding, = (row for row in candidates if row['rawFindingIndex'] == 327)
    raw_warning = finding['raw']
    assert raw_warning['method'] == 'requireRetained' and raw_warning['beginline'] == '543'
    assert raw_warning['path'] == str(CODE) and raw_warning['rule'] == 'AvoidSynchronizedStatement'
    current_source = git('show', f'{core}:{CODE}')
    assert current_source == CODE.read_bytes()
    assert sha(current_source) == finding['sourceSha256'] == raw['sourceInputs'][str(CODE)]
    assert sha(current_source) == physical['sourceInputs'][str(CODE)]
    lines = current_source.decode().splitlines()
    assert lines[542] == finding['actualSourceLine'] == '      synchronized (stateLock) {'
    holding = '\n'.join(lines[541:558])
    proof_call = 'marker.requireRetained();'
    assert holding.count('context.recheck();') == holding.count('gate.verify();') == 2
    assert holding.count(proof_call) == 1 and holding.index('gate.verify();') < holding.index(proof_call)
    assert 'retainedStatus != Status.CLIENT_EXITED_ZERO' in holding
    assert '.retire(' not in holding
    owner = physical['physicalClassHashes']['batch'][TARGET + '$Attempt.class']
    assert owner == prior['attemptClassSha256']
    callers = [n for n, line in enumerate(lines, 1) if line.strip() in ('api.requireRetained(owner);', 'web.requireRetained(owner);')]
    assert callers == [472, 473]
    result = dict(actualExit=0, source=start['source'], sourceCore=core, findingId=327, rule=raw_warning['rule'],
                  path=str(CODE), method='BackupUnitStartClient.Attempt.requireRetained', line=543,
                  sourceSha256=sha(current_source), attemptClassSha256=owner,
                  synchronizedSpanSha256=sha(holding.encode()), staticCallerLines=callers,
                  decision='APPLICABLE_OPEN', basis='Read-only API/Web proof can run the owner callback and retained-resource verification under the same monitor.',
                  nextEvidence='Authorized independent owner-proof success/failure and concurrent lifecycle tests, demonstrating retained observations without a readiness or retirement receipt.',
                  previousUnclassified=32, unclassifiedAfter=31, applicableOpenInOriginal45=14,
                  dynamicTests=0, runtimeReachabilityMeasured=False, externalOperations=0,
                  newFormalAcceptance=0, wholeF03Accepted=False, whole451Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / start['run']
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(sha(p.read_bytes()))


if __name__ == '__main__':
    main()
