"""Read exact archived WebLog Outbox coverage and acquire-site shapes without product execution."""
from pathlib import Path
import re
import runpy
import subprocess

ENTRY = Path(__file__).resolve()
h = runpy.run_path(str(ENTRY.with_name('5189_wbs66_four_module_delta_handoff.py')))
E = h['E']
OUT = E / 'PG39668-p00405-weblog-outbox-before-v1'
WEB = Path('evidence/01_PT/015_NK-WEB-001/evidence')
ARCHIVE = Path('../pgpt-runs/PG379/pg19638-web-outbox-jdbc-twenty-unit-v1/component')
TYPE = 'dev/codex/schubert/nk/web/logging/WebLogOutboxRepository'


def main():
    [original_file] = list(WEB.glob('PG19638*/manifest.json'))
    [independent_file] = list(WEB.glob('PG19638*/pg19646*/manifest.safe.json'))
    original, independent = map(h['load'], (original_file, independent_file))
    assert Path(independent['publicManifest']) == original_file
    assert independent['source'] == original['source'] and not independent['productExecuted']
    assert original['actualExit'] == independent['actualExit'] == independent['terminal']['actualExit'] == 0
    assert original['tests'] == 20 and not any(original[k] for k in ('failures','errors','skipped','aborted'))
    assert original['onlyMemoryCallbackFixtures']
    expected = original['inputHashes']
    main = next(p for p in expected if p.endswith('/WebLogOutboxRepository.java'))
    text = Path(main).read_text()
    assert all(h['ref'](Path(p))['sha256'] == sha for p, sha in expected.items() if p.endswith('.java'))
    old_exec = original_file.parent / 'jacoco.exec'
    inputs = [old_exec, original_file.parent / 'coverage.xml', original_file.parent / 'testcases.safe.xml']
    assert all(h['ref'](p)['sha256'] == original['files'][p.name] for p in inputs)
    binary = ARCHIVE / (TYPE + '.class')
    assert h['ref'](binary)['sha256'] == original['physicalHashes'][TYPE]
    command = h['load'](h['matching_path']('PG39282*/raw-command.json'))[:5] + [str(old_exec), str(binary)]
    raw = subprocess.check_output(command, timeout=40)
    out = OUT / 'unfiltered.tsv'
    with out.open('xb') as f:
        f.write(raw)
    rows = [line.split('\t') for line in raw.decode().splitlines()]
    [cls] = [r for r in rows if r[0] == 'CLASS']
    counts = {kind: {'missed': int(m), 'covered': int(c)}
              for kind, m, c in [v.split(':') for v in cls[6:]]}
    assert cls[2] == original['physicalClassIds'][TYPE] and cls[3] == 'true'
    assert counts['BRANCH']['missed'] > 0
    acquisitions = [(m.start(), 1 + text.count('\n', 0, m.start()), m[1])
                    for m in re.finditer(r'try \((var statement|ResultSet result)\s*=', text)]
    assert [x[2] for x in acquisitions].count('var statement') == 4
    assert [x[2] for x in acquisitions].count('ResultSet result') == 1
    h['write'](OUT / 'manifest.json', dict(actualExit=0, original=h['ref'](original_file),
                 independent=h['ref'](independent_file), physical=h['ref'](binary), historicalSource=original['source'],
                 originalRawCounters=counts, activeMainAndTestsSame=True, acquisitions=acquisitions,
                 originalExecutionArtifacts=[h['ref'](p) for p in inputs], originalExecCombined=0,
                 raw=h['ref'](out), analysisCommand=command, originalProductTestsRepeated=0))
    print(counts)


if __name__ == '__main__':
    main()
