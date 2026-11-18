"""Recover old executable baseline and record required owner acquisition sites."""
from pathlib import Path
import runpy
import subprocess

ENTRY = Path(__file__).resolve()
h = runpy.run_path(str(ENTRY.with_name('5189_wbs66_four_module_delta_handoff.py')))
E = h['E']
OUT = E / 'PG39634-p00405-business-outbox-before-v1'
OLD = Path('evidence/01_PT/006_NK-MSG-002/evidence')
ARCHIVE = Path('../pgpt-runs/PG379/pg21014-outbox-null-oracle-nine-unit-v1/component')
TYPE = 'dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository'


def main():
    post = next(OLD.glob('PG21014*/manifest.json'))
    independent_file = next(OLD.glob('PG21028*/manifest.json'))
    original = h['load'](post)
    independent = h['load'](independent_file)
    assert independent['originalPost'] == h['ref'](post)
    assert original['actualExit'] == independent['actualExit'] == 0
    assert original['tests'] == independent['tests'] == 9 and original['onlyMemoryCallbackFixtures']
    assert not any(original[key] for key in ('failures', 'errors', 'skipped', 'aborted'))
    for name, digest in original['files'].items():
        f = post.parent / name
        if name in ('testcases.safe.xml', 'jacoco.exec', 'coverage.xml'):
            assert h['ref'](f)['sha256'] == digest
    sources = original['inputHashes']
    main_path = next(p for p in sources if p.endswith('/JdbcOutboxRepository.java'))
    current = Path(main_path).read_text()
    assert all(h['sha'](Path(p).read_bytes()) == v for p, v in sources.items() if p.endswith('.java'))
    issuer = ARCHIVE / (TYPE + '.class')
    assert h['ref'](issuer)['sha256'] == original['physicalHashes'][TYPE]
    command = h['load'](h['matching_path']('PG39282*/raw-command.json'))[:5]
    command += [str(post.parent / 'jacoco.exec'), str(issuer)]
    raw = subprocess.check_output(command, timeout=40)
    output = OUT / 'unfiltered.tsv'
    with output.open('xb') as out:
        out.write(raw)
    cls = [row.split('\t') for row in raw.decode().splitlines() if row.startswith('CLASS\t')]
    [stats] = cls
    assert stats[2] == original['physicalClassIds'][TYPE]
    assert stats[3] == 'true'
    counts = {k: {'missed': int(m), 'covered': int(c)} for k, m, c in [v.split(':') for v in stats[6:]]}
    assert counts['BRANCH']['missed'] > 0
    acquired = []
    for n, line in enumerate(current.splitlines(), 1):
        if 'try (PreparedStatement ' in line:
            acquired.append((n, 'statement', line.strip()))
        if 'try (ResultSet ' in line:
            acquired.append((n, 'result', line.strip()))
    assert [x[1] for x in acquired].count('statement') == 4
    assert [x[1] for x in acquired].count('result') == 2
    assert all('requireValue' not in x[2] for x in acquired)
    h['write'](OUT / 'manifest.json', dict(actualExit=0, original=h['ref'](post),
                 originalIndependent=h['ref'](independent_file), unchangedOriginalMainAndFixtureInput=True,
                 historicalSource=original['source'], archivedClass=h['ref'](issuer),
                 sourceOwnershipAbsentNullCheck=acquired, originalRawCounters=counts,
                 oldExecSingle=h['ref'](post.parent / 'jacoco.exec'), analysis=command,
                 output=h['ref'](output), originalNineReexecuted=0, productTestsExecuted=0))
    print(counts)


if __name__ == '__main__':
    main()
