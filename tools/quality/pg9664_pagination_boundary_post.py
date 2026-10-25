"""Independent original XML/source/class/CRC/session post; not another execution of the three tests."""
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
OPS = data.BASE
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
NORMAL = WORK / 'pg9660-pagination-six-compile-v1/snapshot'
RUN = WORK / 'pg9662-pagination-boundary-host-v1'
SLOT = WORK / 'pg9664-pagination-boundary-post-v1'
OUT = BASE / 'PG9664-pagination-boundary-post-v1'
HOST_SHA = 'c5dfb7e4137c0c96833bcba4a3a3c6ec5cba04a54b3134d13b7395d808cbc19e'
NORMAL_SHA = 'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c'
TYPE = 'dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest'
TARGET = 'dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator'
METHODS = {
    'page001SecondPageHasIndependentExpectedBounds',
    'page002MaximumEffectivePageKeepsExactNineDigitArithmetic',
    'page003RejectsIndependentRangeAndOneFieldArithmeticChanges'}
TEST = 'src/schubert-nk-protocol/src/test/java/' + TYPE.replace('.', '/') + '.java'
HELPER = ROOT / 'tools/quality/architecture/PaginationBoundaryCoverageMeasure.java'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    raw = data.read_checked(RUN / 'manifest.safe.json', HOST_SHA)
    assert data.sha((BASE / 'PG9662-pagination-boundary-host-v1/manifest.json').read_bytes()) == HOST_SHA
    normal = data.read_checked(OPS / 'PG9660-pagination-six-compile-v1/manifest.json', NORMAL_SHA)
    assert raw['actualExit'] == normal['actualExit'] == normal['terminal']['actualExit'] == 0
    assert raw['source'] == normal['source'] == SOURCE and normal['testsExecuted'] == 0
    assert raw['begin']['compileManifestSha256'] == NORMAL_SHA and raw['begin']['selectedSuites'] == {'PayloadPaginationBoundaryTest': 3}
    assert len(raw['stages']) == 2 and all(s['actualExit'] == 0 and not s['timedOut'] for s in raw['stages'])
    assert len(raw['cases']) == 3 and Counter(row['name'] for row in raw['cases']) == Counter(METHODS)
    assert all(row['classname'] == TYPE and row['result'] == 'PASS' and row['nonPass'] == [] for row in raw['cases'])
    xml = RUN / 'xml' / ('TEST-' + TYPE + '.xml')
    report = ET.parse(xml).getroot()
    assert report.get('name') == TYPE and {k: int(report.get(k)) for k in ('tests', 'failures', 'errors', 'skipped')} == dict(tests=3, failures=0, errors=0, skipped=0)
    cases = report.findall('testcase')
    assert len(cases) == 3 and {c.get('name') for c in cases} == METHODS and all(c.get('classname') == TYPE and not list(c) for c in cases)
    assert raw['xmlHashes'] == {xml.name: data.sha(xml.read_bytes())}
    summary = RUN / 'xml/summary.safe.txt'
    assert summary.read_text() == 'found=3;started=3;succeeded=3;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN / 'jacoco.exec').read_bytes()) == raw['execSha256']
    for name, digest in raw['begin']['dependencyHashes'].items():
        assert data.sha(Path(name).read_bytes()) == digest
    for name, digest in raw['begin']['testSourceHashes'].items():
        assert data.sha(Path(name).read_bytes()) == digest
    for name, digest in normal['begin']['inputHashes'].items():
        assert data.sha((ROOT / name).read_bytes()) == data.sha((NORMAL / name).read_bytes()) == digest
    assert subprocess.check_output(['git', 'show', SOURCE + ':' + TEST], cwd=ROOT) == (ROOT / TEST).read_bytes()
    assert subprocess.check_output(['git', 'diff', '--name-only', data.SOURCE, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines() == [TEST]
    assert subprocess.check_output(['git', 'diff', '--name-only', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT) == b''
    old = data.read_checked(OPS / data.PINS['normal'][0] / 'manifest.json', data.PINS['normal'][1])
    class_count = 0
    for module, item in normal['jars'].items():
        path = Path(item['path'])
        assert path.parent == NORMAL / ('src/schubert-nk-' + module) / 'target' and data.sha(path.read_bytes()) == item['sha256']
        previous = Path(old['jars'][module]['path'])
        assert data.sha(previous.read_bytes()) == old['jars'][module]['sha256']
        with zipfile.ZipFile(path) as current, zipfile.ZipFile(previous) as prior:
            current_names = [n for n in current.namelist() if n.endswith('.class')]
            prior_names = [n for n in prior.namelist() if n.endswith('.class')]
            assert len(current_names) == len(set(current_names)) and set(current_names) == set(prior_names)
            assert all(current.read(n) == prior.read(n) for n in current_names)
            class_count += len(current_names)
    assert class_count == 1843
    os.umask(0o077)
    SLOT.mkdir()
    with zipfile.ZipFile(normal['jars']['protocol']['path']) as archive:
        assert {n for n in archive.namelist() if n == TARGET + '.class' or n.startswith(TARGET + '$')} == {TARGET + '.class'}
        target = SLOT / 'PayloadSemanticValidator.class'
        with target.open('xb') as stream:
            stream.write(archive.read(TARGET + '.class'))
    helper_sha = data.sha(HELPER.read_bytes())
    tc = ROOT.parent / 'toolchain'
    libraries = [tc / 'm2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc / f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ('asm', 'asm-tree', 'asm-commons')]]
    hashes = {str(path): data.sha(path.read_bytes()) for path in libraries}
    cp = os.pathsep.join(map(str, libraries))
    reader = SLOT / 'reader'
    reader.mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-report', [str(tc / 'jdk-25.0.4/bin/javac'), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', cp, '-d', str(reader), str(HELPER)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('measure-whole-class', [str(tc / 'jdk-25.0.4/bin/java'), '-cp', str(reader) + os.pathsep + cp,
        HELPER.stem, str(RUN / 'jacoco.exec'), str(target)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    lines = (SLOT / 'measure-whole-class.stdout').read_text().splitlines()
    first = lines[0].split('\t')
    assert first[:2] == ['CLASS', TARGET] and len(first) == 3
    counters = {}
    for line in lines[1:]:
        label, kind, missed, covered = line.split('\t')
        assert label == 'COUNTER' and kind not in counters
        counters[kind] = dict(missed=int(missed), covered=int(covered))
    assert set(counters) == {'LINE', 'METHOD', 'CLASS', 'BRANCH'} and any(c['missed'] > 0 for c in counters.values())
    assert data.sha(HELPER.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p, h in hashes.items())
    verify(invocation)
    OUT.mkdir()
    with (OUT / xml.name).open('xb') as stream:
        stream.write(xml.read_bytes())
    with (OUT / 'summary.safe.txt').open('xb') as stream:
        stream.write(summary.read_bytes())
    result = dict(actualExit=0, source=SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), invocation=invocation,
        hostManifestSha256=HOST_SHA, normalManifestSha256=NORMAL_SHA, actualTests=3, suites=1, newTestIds=3,
        failures=0, errors=0, skipped=0, aborted=0, cases=sorted(METHODS),
        testIds=['PT-PRO-002-PAGE001', 'PT-PRO-002-PAGE002', 'PT-PRO-002-PAGE003'],
        testSourceSha256=data.sha((ROOT / TEST).read_bytes()), xmlSha256=data.sha(xml.read_bytes()),
        summarySha256=data.sha(summary.read_bytes()), execSha256=raw['execSha256'],
        wholeSourceUnitCounters=counters, physicalClassSha256=data.sha(target.read_bytes()), crc64=first[2],
        sessionId='PG9662-PROTOCOL-PAGINATION-BOUNDARY', reportHelperSha256=helper_sha, reportLibraryHashes=hashes,
        reportStages=stages, allMainClassCount=1843, allMainBytesUnchangedFromPriorCompile=True,
        oldDynamicResultsTransferred=False, coverageUnion=False, exclusionsAdded=False, requiredWholeFour100=False,
        productTestsExecutedByPost=0, newMain=0, programPtComplete=False, whole451Accepted=False,
        formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0,
        actualNetworkActions=0, actualServiceActions=0)
    data.write(SLOT / 'manifest.safe.json', result)
    data.write(OUT / 'manifest.json', result)
    print(json.dumps(dict(actualExit=0, tests=3, wholeSourceUnitCounters=counters, unchangedMainClasses=1843)))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
