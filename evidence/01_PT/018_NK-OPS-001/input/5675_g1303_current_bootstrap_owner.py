from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

CORE = '2611e1acbd57955d591d52e5348999ea293e068d'
BASE = 'ee27a308b6b7da7bd9744000ee490a8f91956ead'
EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
WBS = Path('documents/400_PGPT/470_PMO')
MAIN = 'src/schubert-nk-bootstrap/src/main/java/'
OUTPUT = EVIDENCE / 'PG41432-g1303-current-bootstrap-owner-v1'


def git(*args):
    return subprocess.check_output(['git', *args])


def load(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': digest(path.read_bytes())}


def tree(commit, path):
    entries = git('ls-tree', '-r', '-z', commit, '--', path).decode().split('\0')
    return {line.partition('\t')[2]: line.split()[2] for line in entries if line}


def write(path, value):
    with path.open('x', encoding='utf-8') as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write('\n')


old_path = next(EVIDENCE.glob('PG26146-*/manifest.json'))
package_path = next(EVIDENCE.glob('PG41322-*/manifest.json'))
audit_path = next(EVIDENCE.glob('PG41314-*/manifest.json'))
classification_path = next(EVIDENCE.glob('PG41320-*/manifest.json'))
inventory_path = WBS / '485_WBS網羅性・受入対応.json'
work_path = WBS / '481_PGPT詳細WBS.json'
old = load(old_path)
old_sources = load(old_path.parent / 'source-owner-testid-candidates.json')
old_path_by_name = {row['path']: row for row in old_sources}
current = load(package_path)['packagingProof']['artifacts']['bootstrap']
source_inventory = tree(CORE, MAIN)
assert len(source_inventory) == 88 == len(tree(current['archiveSource'], MAIN))
assert source_inventory == tree(current['archiveSource'], MAIN)
module_now = tree(CORE, 'src/schubert-nk-bootstrap')
module_before = tree(current['archiveSource'], 'src/schubert-nk-bootstrap')
test_delta = sorted(path for path in set(module_now) | set(module_before) if module_now.get(path) != module_before.get(path))
assert len(test_delta) == 1 and test_delta[0].endswith('/src/test/java/dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraphOrderTest.java')
archive = Path(current['artifact']['path'])
assert ref(archive) == {k: current['artifact'][k] for k in ('path', 'sha256')}
artifacts = {row['path']: row for row in load(inventory_path)['artifacts'] if row['path'].startswith(MAIN)}
assert set(source_inventory) == set(artifacts)
work_items = {row['id']: row for row in load(work_path)['tasks']}
design_paths = [p for p in tree(BASE, 'documents/300_SS') if Path(p).name.startswith('361_')]
assert len(design_paths) == 1
design = design_paths[0]
ss361 = {'path': design, 'source': BASE, 'sha256': digest(git('show', f'{BASE}:{design}'))}

# The archived compiler's ZIP entries provide names and central CRC only.
# No class is opened or passed to a compiler, parser, static analyzer or initializer.
with ZipFile(archive) as jar:
    entries = [info for info in jar.infolist() if info.filename.endswith('.class')]
assert len(entries) == len({entry.filename for entry in entries}) == current['physical'] == 201
outer_to_path = {name[len(MAIN):-5]: name for name in source_inventory}
physical = {name: [] for name in source_inventory}
for entry in entries:
    key = entry.filename[:-6].split('$', maxsplit=1)[0]
    name = outer_to_path[key]
    physical[name].append({'name': entry.filename, 'centralDirectoryCrc32': f'{entry.CRC:08x}'})
assert all(physical.values())
held = {entry['name'] for nested in physical.values() for entry in nested if entry['name'].endswith('FixedNativeCoverageCheckpoint$PublicAgent.class')}
assert len(held) == load(audit_path)['staticallyHeldPhysical'] == 1
assert load(classification_path)['unclassified'] == 0

rows = []
owners = Counter()
for name, blob in sorted(source_inventory.items()):
    item = artifacts[name]
    unit = work_items[item['owner']]
    historical = old_path_by_name.get(name)
    status = 'ADDED_PATH_SINCE_OLD_TRACE'
    if historical:
        status = 'SAME_GIT_INPUT' if git('rev-parse', f"{old['productionCoreMain']}:{name}").decode().strip() == blob else 'CHANGED_GIT_INPUT'
        if historical['owner'] != item['owner']:
            assert (historical['owner'], item['owner']) == ('WBS-P019-01', 'WBS-P018-05')
            assert 'PG23836' in item['basis'] and Path(name).name in ('ServiceDatabaseAdmission.java', 'ServiceDatabaseSource.java')
    owners[item['owner']] += 1
    rows.append({
        'sourcePath': name, 'currentGitBlob': blob, 'history': status,
        'owner': item['owner'], 'historicalOwner': historical['owner'] if historical else None,
        'costOwner': item['costOwner'], 'registryBasis': item.get('basis'),
        'registryRelatedSsc': item.get('relatedSsc'),
        'candidateRegistryTestIds': item.get('testIds', []),
        'rd': unit['rd'], 'ui': unit['ui'], 'ss': unit['ss'],
        'candidateSpecDirectory': unit['evidencePlan']['specDirectory'],
        'endingDependencies': unit['dependencies'],
        'physical': sorted(physical[name], key=lambda row: row['name']),
        'individualOracleAndCurrentRuntime': None,
    })
gone = sorted(set(old_path_by_name) - set(source_inventory))
assert len(rows) == 88 and len(owners) == 9
OUTPUT.mkdir()
table = OUTPUT / 'bootstrap-source-owner-inventory.json'
write(table, rows)
report = {
    'run': OUTPUT.name, 'actualExit': 0, 'terminalAtUTC': datetime.now(timezone.utc).isoformat(),
    'core': CORE, 'previousCore': old['productionCoreMain'], 'jarBuildSource': current['archiveSource'],
    'archive': current['artifact'], 'ss361': ss361, 'artifactTestOnlyDelta': test_delta,
    'preliminaryJoinExits': [1, 1], 'preliminaryJoinCauses': ['Initial join asserted all-module-input equality despite the independently recorded added compiler fixture.', 'Second join assumed every registry row used the basis field, whereas relocation records use historicalPath and relatedSsc.'],
    'references': [ref(path) for path in (
        old_path, old_path.parent / 'source-owner-testid-candidates.json', package_path, audit_path,
        classification_path, inventory_path, work_path,
    )],
    'currentSourceFiles': len(rows), 'currentPhysical': len(entries), 'historicalSources': len(old_sources),
    'historicalPhysical': old['physicalClasses'], 'sourceOwnerCounts': dict(sorted(owners.items())),
    'historyCounts': dict(Counter(row['history'] for row in rows)), 'removedHistoricalPaths': gone,
    'missingSourcesOrOwners': 0, 'heldPhysicalNamesOnly': sorted(held), 'classBodiesRead': 0,
    'testBodiesRead': 0, 'ptExecution': 0, 'coverageNew': False, 'formalDelta': 0, 'wholeG1303': False,
    'open': [
        'Current per-method/individual Test ID and independent assertions are outside this artifact join.',
        'Held native class and same-source runtime remain unresolved.',
        'Actual DB migration/rollback and per-owner current-source 451 ending dependencies remain open.',
    ],
    'table': ref(table), 'script': ref(Path(__file__)),
}
write(OUTPUT / 'manifest.json', report)
print(json.dumps({key: report[key] for key in ('currentSourceFiles', 'currentPhysical', 'sourceOwnerCounts', 'historyCounts', 'removedHistoricalPaths')}, ensure_ascii=False))
