"""Classify original PMD 330 using exact source and static backup caller provenance."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
SCOPE = Path('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform')
CLIENT = SCOPE / 'BackupUnitStartClient.java'
CALLER = SCOPE / 'MorningBackupUnitCycle.java'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    start = json.loads(next(D.glob('647_F03*')).read_bytes())['values']
    assert git('rev-parse', 'HEAD').decode().strip() == start['source']
    inputs = []
    for pin in start['oracleReferences']:
        raw = Path(pin['path']).read_bytes()
        assert sha(raw) == pin['sha256']
        inputs.append(json.loads(raw))
    warnings, original, physical, previous = inputs
    core = start['productionCoreMain']
    assert previous['findingId'] == 328 and previous['unclassifiedAfter'] == 30
    assert previous['applicableOpenInOriginal45'] == 15
    assert previous['sourceCore'] == physical['sourceCore'] == core
    finding, = (r for r in warnings if r['rawFindingIndex'] == 330)
    row = finding['raw']
    assert (row['path'], row['beginline'], row['method'], row['rule']) == (
        str(CLIENT), '598', 'retireAfter', 'AvoidSynchronizedStatement')
    sources = {}
    for p in (CLIENT, CALLER):
        data = git('show', f'{core}:{p}')
        assert data == p.read_bytes() and sha(data) == physical['sourceInputs'][str(p)]
        sources[p] = data
    raw = sources[CLIENT]
    assert sha(raw) == finding['sourceSha256'] == original['sourceInputs'][str(CLIENT)]
    numbered = raw.decode().splitlines()
    assert numbered[597] == finding['actualSourceLine'] == '      synchronized (stateLock) {'
    section = '\n'.join(numbered[596:614])
    order = ('retiring = true;', 'gate.verify();', 'retireUncertain = true;', 'marker.retire();', 'retired = true;',
             'finally', 'retiring = false;')
    assert list(map(section.index, order)) == sorted(map(section.index, order))
    caller_lines = [n for n, row in enumerate(sources[CALLER].decode().splitlines(), 1)
                    if 'attempt.retireAfter(' in row]
    assert caller_lines == [229, 373, 488]
    result = dict(actualExit=0, source=start['source'], sourceCore=core, findingId=330,
                  path=str(CLIENT), line=598, method='BackupUnitStartClient.Attempt.retireAfter',
                  rule=row['rule'], sourceSha256=sha(raw), spanSha256=sha(section.encode()),
                  caller=dict(path=str(CALLER), sourceSha256=sha(sources[CALLER]), callLines=caller_lines),
                  decision='APPLICABLE_OPEN',
                  basis='The separate parent backup caller can reach owner/proof callbacks and resource retirement under the monitor.',
                  nextEvidence='Independent authorized proof of admission, callback/retirement rejection and preservation at concurrent or uncertain terminal boundaries.',
                  priorUnclassified=30, unclassifiedAfter=29, applicableOpenInOriginal45=16,
                  runtimeReachabilityMeasured=False, productTests=0, retirementOperations=0,
                  externalOperations=0, wholeF03Accepted=False, whole451Accepted=False,
                  newFormalAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / start['run']
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(sha(p.read_bytes()))


if __name__ == '__main__':
    main()
