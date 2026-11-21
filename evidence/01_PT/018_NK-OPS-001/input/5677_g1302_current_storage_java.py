from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

ROOT = Path('evidence/01_PT/018_NK-OPS-001/evidence')
OUT = ROOT / 'PG41438-g1302-storage-java-artifact-v1'
WBS = Path('documents/400_PGPT/470_PMO')
MAIN = 'src/schubert-nk-storage/src/main/java/'

def git(*args):
    return subprocess.check_output(['git', *args], timeout=10)

def read(path):
    return json.loads(path.read_bytes())

def refer(path):
    return {'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(ROOT.glob(f'{run}-*/manifest.json'))

def sources(commit):
    return git('ls-tree', '-r', '--name-only', commit, '--', MAIN).decode().splitlines()

context = read(next(WBS.glob('601_*/1812_*.json')))['values']
core, canonical = context['productionCoreMain'], context['canonicalDesignSource']
wbs = WBS / '485_WBS網羅性・受入対応.json'
work = WBS / '481_PGPT詳細WBS.json'
items = {row['id']: row for row in read(work)['tasks']}
registry = {row['path']: row for row in read(wbs)['artifacts'] if row['path'].startswith(MAIN)}
assembly = read(find('PG41322'))['packagingProof']['artifacts']['storage']
historical = read(find('PG26124'))
assert len(registry) == len(sources(core)) == len(sources(assembly['archiveSource'])) == 25
assert set(registry) == set(sources(core)) == set(sources(assembly['archiveSource']))
assert read(find('PG41428'))['actualExit'] == read(find('PG41426'))['actualExit'] == 0

jar = Path(assembly['artifact']['path'])
assert refer(jar)['sha256'] == assembly['artifact']['sha256']
physical = {key[len(MAIN):-5]: [] for key in registry}
with ZipFile(jar) as archive:
    classes = [item for item in archive.infolist() if item.filename.endswith('.class')]
assert len(classes) == len({entry.filename for entry in classes}) == assembly['physical'] == 79
for entry in classes:
    basename = entry.filename[:-6].split('$', maxsplit=1)[0]
    physical[basename].append(entry.filename)
assert all(physical.values())
designs = {}
for path in git('ls-tree', '-r', '-z', '--name-only', canonical, '--', 'documents/300_SS').decode().split('\0')[:-1]:
    number = Path(path).name.split('_', maxsplit=1)[0]
    if number in {'311', '331', '332', '361'}:
        designs[number] = {'path': path, 'sha256': sha256(git('show', f'{canonical}:{path}')).hexdigest()}
assert set(designs) == {'311', '331', '332', '361'}

java_sql = re.compile(r'(?<![a-zA-Z0-9_])java\.sql\.')
legacy = re.compile(r'\bStorageIoException\.preserveFatal\(')
rows = []
sql_sites = []
legacy_sites = []
for path, owner in sorted(registry.items()):
    body = git('show', f'{core}:{path}')
    assert body == git('show', f"{assembly['archiveSource']}:{path}")
    unit = items[owner['owner']]
    rows.append(dict(path=path,sha256=sha256(body).hexdigest(),physical=sorted(physical[path[len(MAIN):-5]]),
        owner=owner['owner'],costOwner=owner['costOwner'],rd=unit['rd'],ui=unit['ui'],ss=unit['ss'],
        specDirectory=unit['evidencePlan']['specDirectory'],individualContractAndRun=None))
    for number, line in enumerate(body.decode().splitlines(), 1):
        if java_sql.search(line):
            sql_sites.append(dict(path=path,line=number))
        if legacy.search(line):
            legacy_sites.append(dict(path=path,line=number))
assert len(sql_sites) == 1 and sql_sites[0]['path'].endswith('/StorageIoException.java')
assert len(legacy_sites) == 3 and all(site['path'].endswith('/OwnedTransferDirectory.java') for site in legacy_sites)
outcome = dict(actualExit=0,run=OUT.name,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    core=core,archiveSource=assembly['archiveSource'],canonicalDesign=canonical,design=designs,
    archive=assembly['artifact'],references=[refer(path) for path in (find('PG26124'),find('PG41322'),
        find('PG41428'),find('PG41426'),wbs,work)], historicalStorageArtifacts=historical['storageModuleArtifacts'],
    currentSource=len(rows),currentPhysical=len(classes),ownerCounts=dict(Counter(row['owner'] for row in rows)),
    rows=rows,oldJavaSqlSourceSites=sql_sites,threeLegacyLowerCallerSourceSites=legacy_sites,
    preliminaryMetadataReadExit=1,preliminaryReadCause='Git quoted Japanese paths without NUL delimiters.',
    rootCauseOrSemanticsFixed=False,classBodyReads=0,productTests=0,realDatabaseOrFdActions=0,formalDelta=0,
    wholeF02=False,wholeG1302=False,whole451=False,script=refer(Path(__file__).resolve().relative_to(Path.cwd())))
OUT.mkdir()
with (OUT/'manifest.json').open('x') as file:
    json.dump(outcome,file,ensure_ascii=False,indent=2)
    file.write('\n')
print(outcome['currentSource'],outcome['currentPhysical'],outcome['ownerCounts'],sql_sites,legacy_sites)
