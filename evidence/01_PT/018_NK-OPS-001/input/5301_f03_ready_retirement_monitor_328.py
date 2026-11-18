"""Determine only the source applicability of the original PMD finding 328."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
BASE = Path('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch')
CLIENT = BASE / 'platform/BackupUnitStartClient.java'
CALLER = BASE / 'file/MorningStartupLaunchOwner.java'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    start = json.loads(next(D.glob('643_F03*')).read_bytes())['values']
    assert git('rev-parse', 'HEAD').decode().strip() == start['source']
    inputs = []
    for pin in start['oracleReferences']:
        data = Path(pin['path']).read_bytes()
        assert sha(data) == pin['sha256']
        inputs.append(json.loads(data))
    warnings, original, physical, previous = inputs
    assert previous['findingId'] == 327 and previous['unclassifiedAfter'] == 31
    assert previous['applicableOpenInOriginal45'] == 14
    core = start['productionCoreMain']
    assert core == previous['sourceCore'] == physical['sourceCore']
    row, = (r for r in warnings if r['rawFindingIndex'] == 328)
    diagnostic = row['raw']
    assert (diagnostic['path'], diagnostic['method'], diagnostic['beginline'], diagnostic['rule']) == (
        str(CLIENT), 'retireReadyAfter', '562', 'AvoidSynchronizedStatement')
    sources = {}
    for path in (CLIENT, CALLER):
        data = git('show', f'{core}:{path}')
        assert data == path.read_bytes() and sha(data) == physical['sourceInputs'][str(path)]
        sources[path] = data
    assert sha(sources[CLIENT]) == row['sourceSha256'] == original['sourceInputs'][str(CLIENT)]
    lines = sources[CLIENT].decode().splitlines()
    assert lines[561] == row['actualSourceLine'] == '      synchronized (stateLock) {'
    method = '\n'.join(lines[560:576])
    assert method.index('retireAfter(before);') < method.index('after.verify();')
    assert method.count('context.recheck();') == 2
    assert '!stdinClosed' in method and '!streamsClosed' in method
    nested = '\n'.join(lines[596:614])
    assert 'synchronized (stateLock)' in nested and 'marker.retire();' in nested
    assert nested.index('retireUncertain = true;') < nested.index('marker.retire();')
    caller = sources[CALLER].decode().splitlines()
    assert [n for n, line in enumerate(caller, 1) if '::retireReadyAfter' in line] == [386, 387, 388]
    assert caller[384].strip() == 'retireCompleted('
    assert 'CompletionPhase.DONE_BEFORE' in caller[392]
    orchestration = '\n'.join(caller[187:220])
    ordered = ('caddy.retire(', 'web.retire(', 'api.retire(', 'CompletionPhase.ALL_RETIRED')
    assert list(map(orchestration.index, ordered)) == sorted(map(orchestration.index, ordered))
    result = dict(actualExit=0, source=start['source'], sourceCore=core, findingId=328,
                  rule=diagnostic['rule'], method='BackupUnitStartClient.Attempt.retireReadyAfter',
                  path=str(CLIENT), line=562, sourceSha256=sha(sources[CLIENT]),
                  synchronizedSpanSha256=sha(method.encode()),
                  caller=dict(path=str(CALLER), sha256=sha(sources[CALLER]), methodReferenceLines=[386, 387, 388]),
                  decision='APPLICABLE_OPEN', basis='The lifecycle caller passes live service callbacks covering both the nested resource retirement and the post-proof under the same monitor.',
                  nextEvidence='Authorized same-owner before/after completion evidence with callback failure and concurrency, plus preserved UNKNOWN if the post-proof fails. No DONE is credited by source review.',
                  previousUnclassified=31, unclassifiedAfter=30, applicableOpenInOriginal45=15,
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
