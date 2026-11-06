"""Independently bind original cases, SourceFile families and unchanged normal bytes."""
from pathlib import Path
import datetime
import hashlib
import io
import json
import struct
import subprocess
import zipfile
import xml.etree.ElementTree as ET


def source_name(data):
    stream = io.BytesIO(data)
    def read(n):
        value = stream.read(n)
        assert len(value) == n
        return value
    def short():
        return struct.unpack('>H', read(2))[0]
    def attrs(pool):
        result = {}
        for _ in range(short()):
            name = pool[short()]
            length = struct.unpack('>I', read(4))[0]
            result.setdefault(name, []).append(read(length))
        return result
    assert read(4) == b'\xca\xfe\xba\xbe'
    read(4)
    pool, index, count = {}, 1, short()
    lengths = {3:4, 4:4, 5:8, 6:8, 7:2, 8:2, 9:4, 10:4, 11:4,
               12:4, 15:3, 16:2, 17:4, 18:4, 19:2, 20:2}
    while index < count:
        tag = read(1)[0]
        if tag == 1:
            pool[index] = read(short()).decode('utf-8')
        else:
            read(lengths[tag])
        index += 2 if tag in (5, 6) else 1
    read(6)
    read(2 * short())
    for _ in range(2):
        for _ in range(short()):
            read(6)
            attrs(pool)
    values = attrs(pool).get('SourceFile', [])
    assert stream.read() == b'' and len(values) <= 1
    return pool[struct.unpack('>H', values[0])[0]] if values else None


r = Path.cwd()
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21878-current-nine-source-physical-evidence-join-v1/manifest.json'
m = load(p)
assert m['actualExit'] == 0 and m['boundSources'] == 9 and not m['pendingSources']
assert m['newProductTests'] == m['newMethods'] == m['newSourceProofs'] == m['newAcceptance'] == 0
assert not m['currentDependencyWholeQualificationTransferred'] and m['effortRate'] is None
matrixp = r/m['matrix']['path']
assert sha(matrixp) == m['matrix']['sha256']
matrix = load(matrixp)
expected = {x['path']:x for x in matrix['rows'] if x['status'] in {
    'SAME_BYTE_COUNTER_CANDIDATE_SCOPE_JOIN_PENDING',
    'HISTORICAL_WHOLE_FACT_CURRENT_JOIN_PENDING',
    'CURRENT_CLASS_HISTORICAL_RECEIPT_METADATA_BOUND'}}
assert set(expected) == {x['path'] for x in m['rows']} and len(expected) == 9
physical_count, cases_by_run, checks = 0, {}, []
for row in m['rows']:
    path = row['path']
    assert row['mainSha256'] == sha(r/path) == expected[path]['sha256']
    assert row['owner'] == row['costOwner'] == expected[path]['owner']
    assert not row['currentDependencyWholeQualificationTransferred'] and not row['newLeafAccepted']
    assert row['newProductTests'] == 0
    jar = Path(row['normalJar']['path'])
    assert sha(jar) == row['normalJar']['sha256']
    relative = path.split('/src/main/java/')[1]
    package = relative.rsplit('/', 1)[0]
    actual = {}
    with zipfile.ZipFile(jar) as archive:
        for entry in archive.namelist():
            if not entry.endswith('.class') or entry.rsplit('/', 1)[0] != package:
                continue
            data = archive.read(entry)
            if source_name(data) == Path(path).name:
                actual[entry[:-6]] = hashlib.sha256(data).hexdigest()
    assert actual == row['physicalFamily'] and actual
    physical_count += len(actual)
    assert len(row['proofs']) == 1
    proof = row['proofs'][0]
    oldp = r/proof['path']
    assert sha(oldp) == proof['sha256']
    old = load(oldp)
    assert old['actualExit'] == old['failures'] == old['errors'] == old['skipped'] == 0
    assert old.get('aborted', 0) == 0
    assert old['tests'] == proof['originalTests']
    assert hashlib.sha256(subprocess.check_output(['git','show',old['source']+':'+path])).hexdigest() == row['mainSha256']
    declared = old.get('physicalHashes') or old.get('physicalClassHashes') or {
        k:v['normalClassSha256'] for k,v in old.get('sourceUnits',{}).items()}
    assert all(declared.get(k) == v for k,v in actual.items())
    xmlp = r/proof['coverageXml']['path']
    assert sha(xmlp) == proof['coverageXml']['sha256'] == old['files'][xmlp.name]
    xml = ET.parse(xmlp)
    packages = [x for x in xml.findall('.//package') if x.get('name') == package]
    assert len(packages) == 1
    sf = [x for x in packages[0].findall('sourcefile') if x.get('name') == Path(path).name]
    assert len(sf) == 1
    counters = {x.get('type'):{'covered':int(x.get('covered')), 'missed':int(x.get('missed'))}
                for x in sf[0].findall('counter')}
    assert counters == proof['sourceFileCounters']
    for kind in ('LINE','METHOD','CLASS'):
        assert counters[kind]['covered'] > 0 and counters[kind]['missed'] == 0
    assert counters.get('BRANCH', {'missed':0})['missed'] == 0
    class_nodes = {x.get('name'):x for x in packages[0].findall('class')}
    for cls in actual:
        assert class_nodes[cls].get('sourcefilename') == Path(path).name
        assert all(int(x.get('missed')) == 0 for x in class_nodes[cls].findall('counter'))
    if proof['path'] not in cases_by_run:
        case_paths = []
        if 'testcases.safe.xml' in old['files']:
            cp = oldp.parent/'testcases.safe.xml'
            assert sha(cp) == old['files'][cp.name]
            case_paths.append(cp)
        else:
            for raw, pin in old['originalXmlPins'].items():
                cp = oldp.parent/Path(raw).name
                public_pin = old['files'].get(Path(raw).name)
                if public_pin is not None:
                    assert cp.is_file() and sha(cp) == public_pin
                else:
                    cp = Path(raw)
                    assert sha(cp) == pin
                case_paths.append(cp)
        cases = []
        for cp in case_paths:
            root = ET.parse(cp)
            for case in root.findall('.//testcase'):
                assert not any(case.find(t) is not None for t in ('failure','error','skipped'))
                cases.append((case.get('classname'), case.get('name')))
        assert len(cases) == old['tests'] and len(set(cases)) == len(cases)
        cases_by_run[proof['path']] = dict(tests=len(cases), files=[
            dict(path=str(cp),sha256=sha(cp)) for cp in case_paths])
    checks.append(dict(path=path, physicalClasses=len(actual), originalManifest=proof['path'],
                       originalCaseCount=old['tests'], sourceCounters=counters))
assert len(cases_by_run) == 8 and set(cases_by_run) == set(m['distinctOriginalRuns'])
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21880-nine-source-join-independent-post-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(),
             checkerSource=head, checkerSha256=sha(Path(__file__)), observerSource=m['observerSource'],
             productionCoreMain=m['productionCoreMain'], original=dict(path=str(p.relative_to(r)),sha256=sha(p)),
             boundSources=9, physicalClasses=physical_count, distinctOriginalRuns=cases_by_run,
             checks=checks, currentDependencyWholeQualificationTransferred=False,
             newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,
             wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,boundSources=9,physicalClasses=physical_count,
                      originalRuns=8,manifestSha256=sha(out/'manifest.json'))))
