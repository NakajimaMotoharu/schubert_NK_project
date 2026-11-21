from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PMO = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
OUT = ROOT / 'PG41442-scr004-order-limit-evidence-v1'
WEB = 'src/schubert-nk-web/src/'
PROTOCOL = 'src/schubert-nk-protocol/src/main/java/'
NAMESPACE = 'dev/codex/schubert/nk/'
CONTEXT = json.loads(next(PMO.glob('1819_*')).read_bytes())['values']

def source(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], timeout=10)

def pin(path):
    return {'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(ROOT.glob(run + '-*/manifest.json'))

def read(path):
    return json.loads(path.read_bytes())

old_path, post_path, package_path = (find(run) for run in ('PG38002', 'PG38004', 'PG41322'))
old, post, package = map(read, (old_path, post_path, package_path))
record = next(PMO.glob('156_*'))
assert post['source'] == old['source'] == read(record)['values']['source']
assert old['actualExit'] == post['actualExit'] == 0 and old['tests'] == post['tests'] == 32
assert all(old[key] == 0 for key in ('failures', 'errors', 'skipped', 'notRun'))

web_names = ['web/view/GameListViewModel', 'web/view/TopBarViewModel', 'web/session/SessionPrincipal']
paths = [WEB+'main/java/'+NAMESPACE+name+'.java' for name in web_names]
fixture = WEB+'test/java/'+NAMESPACE+'web/view/ScenarioHierarchyViewModelTest.java'
template = WEB+'main/resources/templates/scenarios.html'
paths += [fixture,template,'pom.xml','src/schubert-nk-web/pom.xml','src/schubert-nk-protocol/pom.xml']
source_digests = {}
for path in paths:
    current = source(CONTEXT['source'], path)
    assert current == source(old['source'], path), path
    source_digests[path] = sha256(current).hexdigest()

protocol = package['packagingProof']['artifacts']['protocol']
archive = Path(protocol['artifact']['path'])
assert pin(archive) == {key:protocol['artifact'][key] for key in ('path','sha256')}
names = ['protocol/layout/scenario/GameRecord',
         'protocol/layout/PayloadRecord',
         'protocol/layout/TypedFieldValues',
         'protocol/layout/semantic/GameCode',
         'protocol/layout/semantic/UserRole',
         'protocol/header/AuthenticationContext']
exact_classes = {}
with ZipFile(archive) as jar:
    for name in names:
        binary = NAMESPACE+name+'.class'
        digest = sha256(jar.read(binary)).hexdigest()
        assert digest == post['allPhysicalHashes'][binary], binary
        path = PROTOCOL+NAMESPACE+name+'.java'
        assert source(CONTEXT['productionCoreMain'],path) == source(protocol['archiveSource'],path), path
        exact_classes[binary]=digest

design = CONTEXT['canonicalDesignSource']
all_docs = subprocess.check_output(['git','ls-tree','-r','--name-only','-z',design,'--','documents']).decode().split('\0')
ss, ui = [next(p for p in all_docs if p.startswith(prefix) and Path(p).name.startswith(number+'_'))
          for prefix,number in (('documents/300_SS/','313'),('documents/200_UI/','234'))]
bound = {p:sha256(source(design,p)).hexdigest() for p in (ss,ui)}
assert 'SCR004の0件は一覧として空結果文言' in source(design,ss).decode()
assert re.search(r'GAMRSP01[^\n]*最大10件',source(design,ui).decode())

test_names = {
    'web182GameDisplay()':'USER/ADMIN、code・title・固定hrefの独立literal',
    'web191ListSizeBoundaries()':'0件・10件を許容し11件は固定診断で拒否',
    'web192PreserveSourceOrder()':'入力の逆順を二件とも保持',
}
xml = post_path.parent/'xml'/'TEST-junit-jupiter.xml'
assert pin(xml)['sha256'] == post['publicXmlExports'][xml.name]['sha256']
cases = {x.attrib['name']:x for x in ET.parse(xml).getroot().findall('testcase')
         if x.attrib['classname'].endswith('.ScenarioHierarchyViewModelTest')}
assert len(cases) == 12
assert all(name in cases and not any(cases[name].find(t) is not None for t in ('failure','error','skipped'))
           for name in test_names)

raw = post_path.parent/'unfiltered.stdout'
assert pin(raw)['sha256'] == post['files'][raw.name]
classes = ['CLASS\t'+NAMESPACE+name+'\t' for name in ('web/view/GameListViewModel','web/view/GameListViewModel$Card')]
counters = [line.split('\t') for line in raw.read_text().splitlines() if line.startswith(tuple(classes))]
assert len(counters) == 2 and all(line[3] == 'true' for line in counters)
target = {}
for line in counters:
    target[line[1]]={kind:list(map(int,[missed,hit])) for entry in line[6:]
                     for kind,missed,hit in (entry.split(':'),)}
    assert all(data[0] == 0 for data in target[line[1]].values())
manifest = dict(actualExit=0,run=OUT.name,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    currentCore=CONTEXT['productionCoreMain'],designSource=design,originalUnitSource=old['source'],
    originalCore=old['sourceCore'],originalUnitCases=32,localHierarchyCases=12,
    sourceDigests=source_digests,canonicalDocuments=bound,protocolArtifact=pin(archive),
    exactProtocolPhysical=exact_classes,existingCaseOracle=test_names,originalModelRawCounters=target,
    originalRuntimeEvidence=[pin(p) for p in (record,old_path,post_path,xml,raw,package_path)],
    initialAuditExit=1,initialAuditReason='The exported XML digest is in a nested SHA-256 object.',
    currentWebRepackaged=False,newTests=0,replayedTests=0,previousCurrentCoverageMerged=False,
    newFormalAcceptance=0,whole451=False,originalConditionalPriceActivated=False,
    withheld=['Current HTTP/controller empty-result behavior and 0102 termination',
              'Current Browser and actual NK CHR', 'Full source and ending P015-02/451 proof'],
    script=pin(Path(__file__).resolve().relative_to(Path.cwd())))
OUT.mkdir()
with (OUT/'manifest.json').open('x',encoding='utf-8') as file:
    json.dump(manifest,file,ensure_ascii=False,indent=2)
    file.write('\n')
print(len(source_digests),len(exact_classes),list(test_names),len(target))
