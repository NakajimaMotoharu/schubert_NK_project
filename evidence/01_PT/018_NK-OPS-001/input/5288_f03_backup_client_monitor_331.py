"""Classify only original PMD index 331 from preserved proofs and a fixed Java span."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TARGET = 'dev/codex/schubert/nk/batch/platform/BackupUnitStartClient'
MAIN = Path('src/schubert-nk-batch/src/main/java') / (TARGET + '.java')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def main():
    start = json.loads(next(D.glob('621_F03*')).read_bytes())['values']
    assert start['source'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert all(ref(r['path']) == r for r in start['oracleReferences'])
    findings, original, physical, previous = (json.loads(Path(r['path']).read_bytes()) for r in start['oracleReferences'])
    core = start['productionCoreMain']
    assert core == previous['sourceCore'] == physical['sourceCore']
    assert previous['unclassifiedAfter'] == 34 and previous['cumulativeApplicableInOriginal45'] == 11
    hit, = [r for r in findings if r['rawFindingIndex'] == 331]
    assert hit['raw']['path'] == str(MAIN) and hit['raw']['rule'] == 'AvoidSynchronizedStatement'
    assert hit['raw']['method'] == 'awaitClient' and hit['raw']['beginline'] == '618'
    actual = subprocess.check_output(['git', 'show', f'{core}:{MAIN}'], timeout=25)
    assert actual == MAIN.read_bytes()
    assert sha(actual) == hit['sourceSha256'] == original['sourceInputs'][str(MAIN)] == physical['sourceInputs'][str(MAIN)]
    lines = actual.decode().splitlines()
    assert lines[617] == hit['actualSourceLine'] == '      synchronized (stateLock) {'
    body = '\n'.join(lines[617:660])
    assert 'process.waitFor(' in body and 'TimeUnit.SECONDS.toNanos(120)' in body
    assert 'getOutputStream(), "start stdin").close()' in body
    assert 'closeBoth(stdout, stderr)' in body and 'retainedStatus =' in body and 'poisoned = true;' in body
    owners = {name: digest for name, digest in physical['physicalClassHashes']['batch'].items()
              if name.removesuffix('.class').split('$', 1)[0] == TARGET}
    assert TARGET+'.class' in owners and TARGET+'$Attempt.class' in owners
    result = dict(actualExit=0, source=start['source'], sourceCore=core, rawIndex=331, target=ref(MAIN),
                  synchronizedSpanSha256=sha(body.encode()), startLine=618, physical=owners,
                  decision='APPLICABLE_OPEN', reason='Finite wait, stream closing and UNKNOWN/status mutation occur with the same monitor held.',
                  outstanding='Owned wait/streams/UNKNOWN and concurrent lifecycle requirements need independently qualified postconditions before changing synchronization.',
                  priorUnclassified=34, unclassifiedAfter=33, cumulativeApplicableInOriginal45=12,
                  otherHoldRowsUnchanged=True, wholeF03Accepted=False, whole451Accepted=False,
                  productTests=0, runtimeOperations=0, newAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    out = E / start['run']
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(p))


if __name__ == '__main__':
    main()
