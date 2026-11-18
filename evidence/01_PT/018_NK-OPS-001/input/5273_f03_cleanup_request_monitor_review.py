"""Relate five saved PMD monitor sites to the current public source, without running it."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TARGET = ('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/'
          'file/CleanupWorkerRequestFiles.java')
DESIGN = next(Path('documents/300_SS').rglob('343_*.md'))
SITES = {
    132: ('requireClear', 262, 278, ('root.atDirectory(', 'Files.newDirectoryStream('),
          'Directory enumeration and its guard are inside the held monitor.'),
    133: ('requireOwnedNames', 292, 314, ('Files.newDirectoryStream(', 'observed.equals(expected)'),
          'The monitor covers the enumeration and membership check as one operation.'),
    134: ('prepareBytes', 330, 362, ('write(held, content)', 'root.atPartHandle('),
          'Owned staging write and before/after byte and identity confirmation run while held.'),
    135: ('readBytes', 374, 395, ('read(p, before.metadata().size(), bytes)', 'atExistingEntryHandle('),
          'Borrowed I/O and its identity comparison are protected by the same monitor.'),
    136: ('retireBytes', 410, 427, ('actual = readBytes();', 'Arrays.equals(expected, actual)'),
          'Entry ownership comparison and a reentrant call to the same monitored read are held.'),
}


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=35)


def main():
    start = read(next(D.glob('586_F03*.json')))
    v = start['values']
    assert git('rev-parse', 'HEAD').decode().strip() == v['source']
    pins = v['oracleReferences']
    assert all(ref(pin['path']) == pin for pin in pins)
    remaining, raw, build, prior = (read(pin['path']) for pin in pins)
    core = v['productionCoreMain']
    assert prior['sourceCore'] == build['sourceCore'] == core
    assert len(remaining) == prior['effect']['historicalUnclassifiedTotal'] == 45
    assert prior['effect']['unclassifiedAfterReviewedSubset'] == 41
    content = git('show', f'{core}:{TARGET}')
    source_sha = sha(content)
    assert content == Path(TARGET).read_bytes() == git('show', f"{v['source']}:{TARGET}")
    assert raw['sourceInputs'][TARGET] == build['sourceInputs'][TARGET] == source_sha
    lines = content.decode().splitlines()
    selected = {row['rawFindingIndex']: row for row in remaining if row['raw']['path'] == TARGET}
    assert set(selected) == set(SITES)
    all_site_lines = [i for i, line in enumerate(lines, 1) if line.strip() == 'synchronized (lock) {']
    assert all_site_lines == [site[1] for site in SITES.values()]
    decisions = []
    for index, (method, first, last, markers, reason) in SITES.items():
        found = selected[index]
        item = found['raw']
        assert found['sourceSha256'] == source_sha
        assert item['method'] == method and int(item['beginline']) == first
        assert item['rule'] == 'AvoidSynchronizedStatement' and found['actualSourceLine'] == lines[first - 1]
        span = '\n'.join(lines[first - 1:last])
        assert all(marker in span for marker in markers)
        decisions.append(dict(index=index, method=method, line=first, witnessSpanSha256=sha(span.encode()),
                              status='APPLICABLE_OPEN', reason=reason))
    canon = git('rev-parse', 'origin/main').decode().strip()
    design = git('show', f'{canon}:{DESIGN}')
    assert any('SSC104/PG325' in row and '全byte・inode・force/dir sync' in row
               for row in design.decode().splitlines())
    outer = 'dev/codex/schubert/nk/batch/file/CleanupWorkerRequestFiles'
    compiled = {name: item for name, item in build['physicalClassHashes']['batch'].items()
                if name == outer + '.class' or name.startswith(outer + '$')}
    assert sorted(name.split('/')[-1] for name in compiled) == [
        'CleanupWorkerRequestFiles$OwnerSource.class', 'CleanupWorkerRequestFiles$StartupName.class',
        'CleanupWorkerRequestFiles$StartupSource.class', 'CleanupWorkerRequestFiles.class',
    ]
    result = dict(actualExit=0, sourceCore=core, source=ref(TARGET), evidence=pins, decisions=decisions,
                  priorPlanUnclassified=41, afterSubsetUnclassified=36, knownApplicableInOriginal45=9,
                  originalRawRetained=True, noReanalysis=True, sameMonitorReentrantRead=True,
                  preparationExit1='Checked compile inventory also contains StartupSource metadata.',
                  priorRootUnclassifiedUntouched=10, physicalReceipt=compiled,
                  design=dict(path=str(DESIGN), source=canon, sha256=sha(design)),
                  productTests=0, heldOperations=0, actualRuntimePost=0, formalUpdated=False,
                  wholeF03Accepted=False, whole451Accepted=False, newAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    out = E / v['run']
    out.mkdir()
    path = out / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(path), result['afterSubsetUnclassified'])


if __name__ == '__main__':
    main()
