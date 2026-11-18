"""Bind two previously unclassified monitor findings to exact public source, without execution."""
from datetime import datetime, timezone
from pathlib import Path
import json
import runpy

A = runpy.run_path(str(Path(__file__).with_name('5273_f03_cleanup_request_monitor_review.py')))
D, E, DESIGN = (A[key] for key in ('D', 'E', 'DESIGN'))
read, sha, ref, git = (A[key] for key in ('read', 'sha', 'ref', 'git'))
PACKAGE = 'dev/codex/schubert/nk/batch/platform'
SITES = {
    343: ('BackupUnitTermination', 'quiescent', 118, 148, 'observations.read()',
          'namespace()', 'The monitor encloses borrowed read and repeated same-ownership namespace observations.'),
    387: ('MaintenanceUnitStopClient', 'awaitClient', 177, 208, 'process.waitFor(',
          'closeBoth(stdout, stderr)', 'Finite process wait and owned stream closing remain inside the same monitor.'),
}


def main():
    s = read(next(D.glob('590_F03*.json')))
    values = s['values']
    assert git('rev-parse', 'HEAD').decode().strip() == values['source']
    assert all(ref(row['path']) == row for row in values['oracleReferences'])
    remaining, raw, normal, prior, old = (read(row['path']) for row in values['oracleReferences'])
    core = values['productionCoreMain']
    assert prior['sourceCore'] == normal['sourceCore'] == core
    assert prior['afterSubsetUnclassified'] == 36
    by_id = {row['rawFindingIndex']: row for row in remaining}
    found = []
    for index, (clazz, method, first, last, call, other, reason) in SITES.items():
        path = f'src/schubert-nk-batch/src/main/java/{PACKAGE}/{clazz}.java'
        current = git('show', f'{core}:{path}')
        row = by_id[index]
        assert current == Path(path).read_bytes()
        assert sha(current) == raw['sourceInputs'][path] == normal['sourceInputs'][path] == row['sourceSha256']
        lines = current.decode().splitlines()
        assert row['raw']['method'] == method and int(row['raw']['beginline']) == first
        assert row['raw']['rule'] == 'AvoidSynchronizedStatement' and row['raw']['path'] == path
        assert lines[first-1] == row['actualSourceLine'] and 'synchronized (stateLock)' in lines[first-1]
        span = '\n'.join(lines[first-1:last])
        assert call in span and other in span
        physical = {name: digest for name, digest in normal['physicalClassHashes']['batch'].items()
                    if name.removesuffix('.class').split('$', 1)[0] == PACKAGE + '/' + clazz}
        assert len(physical) >= 2 and PACKAGE + '/' + clazz + '.class' in physical
        found.append(dict(index=index, method=method, source=ref(path), spanSha256=sha(span.encode()),
                          line=first, decision='APPLICABLE_OPEN', reason=reason, physical=physical))
    companion, = [row for row in old if row['rawFindingIndex'] == 386]
    assert companion['decision'] == 'NOT_APPLICABLE_JAVA25_NONBLOCKING_MEMORY_ATOMICITY'
    assert companion['sourceSha256'] == found[1]['source']['sha256'] and companion['method'] == 'status'
    canonical = git('rev-parse', 'origin/main').decode().strip()
    contract = git('show', f'{canonical}:{DESIGN}')
    assert 'SSC124'.encode() in contract and 'SSC100'.encode() in contract
    result = dict(actualExit=0, sourceCore=core, decisions=found, originalRawRetained=True,
                  priorUnclassified=36, unclassifiedAfter=34, cumulativeApplicableInOriginal45=11,
                  unchangedCompanion386=companion, protectedOriginalCountersUntouched=True,
                  canonicalDesign=dict(path=str(DESIGN), source=canonical, sha256=sha(contract)),
                  references=values['oracleReferences'], actualRuntimeOperations=0, productTests=0,
                  actualStaticToolReplayed=0, wholeF03Accepted=False, whole451Accepted=False,
                  newAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    out = E / values['run']
    out.mkdir()
    file = out / 'manifest.json'
    file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(file))


if __name__ == '__main__':
    main()
