from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
OUTPUT = EVIDENCE / 'PG41440-f03-ssc447-and-current-protocol-cases-v1'
START = next(Path('documents/400_PGPT/470_PMO').glob('601_*/1815_*.json'))

def pin(path):
    return {'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(EVIDENCE.glob(run + '-*/manifest.json'))

def read(path):
    return json.loads(path.read_bytes())

def git(*args):
    return subprocess.check_output(['git', *args], timeout=15)

context = read(START)['values']
core = context['productionCoreMain']
old_source, current_source = find('PG36620'), find('PG41304')
legacy, current = read(old_source), read(current_source)
expected_legacy, expected_current = 152, 171
assert legacy['actualExit'] == current['actualExit'] == 0
assert legacy['tests'] == expected_legacy and current['ordinaryTests'] == expected_current
assert sum(legacy[key] for key in ('failures', 'errors', 'skipped')) == 0
assert sum(current[key] for key in ('failures', 'errors', 'skipped', 'notRun')) == 0
assert git('diff', '--name-only', current['source'], core, '--', 'pom.xml', 'src/schubert-nk-protocol') == b''
assert git('diff', '--name-only', current['source'], context['source'], '--', 'pom.xml', 'src/schubert-nk-protocol') == b''
new_roster = current_source.parent / 'cases.json'
record = next(row for row in current['evidence'] if row['path'].endswith('/cases.json'))
assert pin(new_roster)['sha256'] == record['sha256']
older_cases = {(case['classname'], case['name'].removesuffix('()')) for case in legacy['cases']}
current_rows = read(new_roster)
current_cases = {(case['className'], case['method']) for case in current_rows}
assert len(older_cases) == len(legacy['cases']) == expected_legacy
assert len(current_cases) == len(current_rows) == expected_current
assert all(not any(row[key] for key in ('failure', 'error', 'skipped')) for row in legacy['cases'])
assert all(row['outcome'] == 'PASS' for row in current_rows)
physical = current_source.parent / 'unfiltered.tsv'
assert pin(physical)['sha256'] == next(row['sha256'] for row in current['evidence'] if row['path'].endswith('/unfiltered.tsv'))
classes = [line.split('\t') for line in physical.read_text().splitlines() if line.startswith('CLASS\t')]
assert len(classes) == current['jarPhysicalCount'] == 176
misses = {}
for key in ('LINE', 'METHOD', 'CLASS', 'BRANCH', 'INSTRUCTION'):
    misses[key] = sum(int(col.split(':')[1]) for cells in classes for col in cells[6:] if col.startswith(key + ':'))
not_matched = sorted(older_cases - current_cases)
only_current = sorted(current_cases - older_cases)
matches = older_cases & current_cases
receipt = dict(actualExit=0,run=OUTPUT.name,terminalAtUTC=datetime.now(timezone.utc).isoformat(),core=core,
    ssc447OriginalProductSource=legacy['begin']['productionCoreMain'],separateCurrentProtocolRun=current['run'],
    currentProtocolRunSource=current['source'],currentInputDiff=0,originalSSC447Results=expected_legacy,
    currentProtocolResults=expected_current,matchedNameAndSuite=len(matches),
    originalAbsentByExactName=not_matched,currentOnlyByExactName=only_current,
    matchedBySuite=dict(sorted(Counter(name for name, _ in matches).items())),physicalClasses=len(classes),
    currentProtocolRawMisses=misses,versionsAreSeparateRuns=True,sharedFixtureEffectsAuthorizedElsewhere=False,
    oldDeficitsRetained=True,executionsStarted=0,currentProductTestsAdded=0,
    roleReceiptsAcknowledged=None,wholeSixF03=False,whole451=False,formalDelta=0,
    witnesses=[pin(path) for path in (old_source, current_source, new_roster, physical, find('PG40590'))],
    script=pin(Path(__file__).resolve().relative_to(Path.cwd())))
OUTPUT.mkdir()
with (OUTPUT / 'manifest.json').open('x', encoding='utf-8') as file:
    json.dump(receipt, file, ensure_ascii=False, indent=2)
    file.write('\n')
print(receipt['matchedNameAndSuite'],len(not_matched),len(only_current),misses)
