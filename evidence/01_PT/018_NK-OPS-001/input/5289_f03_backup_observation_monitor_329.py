"""Classify original PMD finding 329 against the exact public source and report."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TARGET = 'dev/codex/schubert/nk/batch/platform/BackupUnitStartClient'
CURRENT = Path('src/schubert-nk-batch/src/main/java') / (TARGET + '.java')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], timeout=25)


def main():
    start = json.loads(next(D.glob('624_F03*')).read_bytes())['values']
    assert git('rev-parse', 'HEAD').decode().strip() == start['source']
    packages = []
    for pin in start['oracleReferences']:
        data = Path(pin['path']).read_bytes()
        assert sha(data) == pin['sha256']
        packages.append(json.loads(data))
    rows, raw, physical, previous = packages
    core = start['productionCoreMain']
    assert previous['sourceCore'] == physical['sourceCore'] == core
    assert previous['unclassifiedAfter'] == 33 and previous['cumulativeApplicableInOriginal45'] == 12
    (finding,) = (row for row in rows if row['rawFindingIndex'] == 329)
    warning = finding['raw']
    assert warning['path'] == str(CURRENT) and warning['method'] == 'preserveObservation'
    assert warning['beginline'] == '580' and warning['rule'] == 'AvoidSynchronizedStatement'
    source = git('show', f'{core}:{CURRENT}')
    assert source == CURRENT.read_bytes()
    assert sha(source) == finding['sourceSha256'] == raw['sourceInputs'][str(CURRENT)]
    assert sha(source) == physical['sourceInputs'][str(CURRENT)]
    lines = source.decode().splitlines()
    assert lines[579] == finding['actualSourceLine'] == '      synchronized (stateLock) {'
    span = '\n'.join(lines[578:590])
    assert span.index('retireUncertain = true;') < span.index('marker.closeObservation();')
    assert 'marker.retire(' not in span
    assert 'public void closeObservation() throws IOException {\n                      marker.close();' in '\n'.join(lines[325:330])
    assert 'public void closeObservation() throws IOException {\n        fence.verify();' in '\n'.join(lines[492:497])
    (attempt,) = (digest for name, digest in physical['physicalClassHashes']['batch'].items()
                  if name == TARGET + '$Attempt.class')
    result = dict(
        actualExit=0, source=start['source'], sourceCore=core, findingId=329,
        rule=warning['rule'], method='BackupUnitStartClient.Attempt.preserveObservation',
        path=str(CURRENT), sourceSha256=sha(source), line=580, attemptClassSha256=attempt,
        synchronizedSpanSha256=sha(span.encode()),
        decision='APPLICABLE_OPEN',
        basis='Normal allowed service branch changes the uncertainty flag and calls a close or proof recheck while holding stateLock.',
        nextEvidence='Qualified owner and independent close-success, close-failure, repeated/concurrent observation and no retirement receipt conditions.',
        previousUnclassified=33, unclassifiedAfter=32, applicableOpenInOriginal45=13,
        runtimeReachabilityMeasured=False, dynamicTests=0, externalOperations=0,
        newFormalAcceptance=0, wholeF03Accepted=False, whole451Accepted=False,
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / start['run']
    out.mkdir()
    path = out / 'manifest.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(sha(path.read_bytes()))


if __name__ == '__main__':
    main()
