from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PMO = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
OUT = ROOT / 'PG41448-scr010-watch-pure-display-evidence-v1'
WEB = 'src/schubert-nk-web/src/'
PROTOCOL = 'src/schubert-nk-protocol/src/main/java/'
NAMESPACE = 'dev/codex/schubert/nk/'
CONTEXT = json.loads(next(PMO.glob('1828_*')).read_bytes())['values']

def source(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], timeout=10)

def pin(path):
    return {'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(ROOT.glob(run + '-*/manifest.json'))

def read(path):
    return json.loads(path.read_bytes())

post_path, package_path, record = (find(run) for run in ('PG38114', 'PG41322','PG38116'))
old_path=post_path.parent/'unit-manifest.json'
old, post, package = map(read, (old_path, post_path, package_path))
assert post['source'] == old['source'] == read(record)['source']
assert old['actualExit'] == post['actualExit'] == 0 and old['tests'] == post['tests'] == 4
assert all(old[key] == 0 for key in ('failures', 'errors', 'skipped', 'notRun'))

web_names = ['web/view/AnimationWatchViewModel', 'web/view/TopBarViewModel', 'web/session/SessionPrincipal']
paths = [WEB+'main/java/'+NAMESPACE+name+'.java' for name in web_names]
fixture = WEB+'test/java/'+NAMESPACE+'web/view/AnimationWatchPublicContractTest.java'
template = WEB+'main/resources/templates/animation-watch.html'
paths += [fixture,template,'pom.xml','src/schubert-nk-web/pom.xml','src/schubert-nk-protocol/pom.xml']
source_digests = {}
for path in paths:
    current = source(CONTEXT['source'], path)
    assert current == source(old['source'], path), path
    source_digests[path] = sha256(current).hexdigest()

protocol = package['packagingProof']['artifacts']['protocol']
archive = Path(protocol['artifact']['path'])
assert pin(archive) == {key:protocol['artifact'][key] for key in ('path','sha256')}
names = ['protocol/layout/media/VideoDescriptorResponseData',
         'protocol/layout/PayloadData',
         'protocol/layout/TypedFieldValues',
         'protocol/layout/semantic/VideoCategory',
         'protocol/layout/semantic/DisplayPath',
         'protocol/layout/semantic/RelativePath',
         'protocol/layout/semantic/Sha256Hex',
         'protocol/layout/semantic/MediaMimeType',
         'protocol/layout/semantic/ContentDisposition',
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
          for prefix,number in (('documents/300_SS/','313'),('documents/200_UI/','235'))]
bound = {p:sha256(source(design,p)).hexdigest() for p in (ss,ui)}
assert 'animation-watch.html' in source(design,ss).decode()
assert 'VIDRSP01' in source(design,ui).decode()

test_names = {
    'public001AllCategoryNavigationAndRoles()':'4カテゴリ・2役割に独立の戻り先リテラル',
    'public002IndependentUtf8LogicalIdVector()':'UTF-8の固定期待リンク',
    'public003NullAndInvalidLogicalIdBoundaries()':'null境界と空ID・dot/dotdotを純値で拒否',
    'public004ImmutableClosedDisplayMap()':'表示用7キー、不変、表示外値を公開しない',
}
xml = post_path.parent/'xml'/'TEST-junit-jupiter.xml'
assert pin(xml)['sha256'] == post['publicXmlExports'][xml.name]['sha256']
cases = {x.attrib['name']:x for x in ET.parse(xml).getroot().findall('testcase')
         if x.attrib['classname'].endswith('.AnimationWatchPublicContractTest')}
assert len(cases) == 4
assert all(name in cases and not any(cases[name].find(t) is not None for t in ('failure','error','skipped'))
           for name in test_names)

raw = post_path.parent/'unfiltered.stdout'
assert pin(raw)['sha256'] == post['files'][raw.name]
classes = ['CLASS\t'+NAMESPACE+name+'\t' for name in ('web/view/AnimationWatchViewModel',)]
counters = [line.split('\t') for line in raw.read_text().splitlines() if line.startswith(tuple(classes))]
assert len(counters) == 1 and all(line[3] == 'true' for line in counters)
target = {}
for line in counters:
    target[line[1]]={kind:list(map(int,[missed,hit])) for entry in line[6:]
                     for kind,missed,hit in (entry.split(':'),)}
    assert all(data[0] == 0 for data in target[line[1]].values())
manifest = dict(actualExit=0,run=OUT.name,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    currentCore=CONTEXT['productionCoreMain'],designSource=design,originalUnitSource=old['source'],
    originalCore=old['sourceCore'],originalUnitCases=4,
    sourceDigests=source_digests,canonicalDocuments=bound,protocolArtifact=pin(archive),
    exactProtocolPhysical=exact_classes,existingCaseOracle=test_names,originalModelRawCounters=target,
    originalRuntimeEvidence=[pin(p) for p in (record,old_path,post_path,xml,raw,package_path)],
    currentWebRepackaged=False,newTests=0,replayedTests=0,previousCurrentCoverageMerged=False,
    newFormalAcceptance=0,whole451=False,originalConditionalPriceActivated=False,
    withheld=['Current Anime HTTP/access, media streaming and opening selection',
              'Current Browser and actual NK CHR', 'Full source and ending P015-02/451 proof'],
    script=pin(Path(__file__).resolve().relative_to(Path.cwd())))
OUT.mkdir()
with (OUT/'manifest.json').open('x',encoding='utf-8') as file:
    json.dump(manifest,file,ensure_ascii=False,indent=2)
    file.write('\n')
print(len(source_digests),len(exact_classes),list(test_names),len(target))
