"""Independent genuine five-method result/counter/static/source join; no target replay."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify
from coverage_session_schema import parse, selftest
from class_counter_applicability import classify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg10156_credloc_preflight import TEST, BINARY, SOURCE


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10160-credloc-oracle-post-v1'
    slot = data.ROOT.parent/'pgpt-runs/PG379/pg10160-credloc-oracle-post-v1'
    run = data.ROOT.parent/'pgpt-runs/PG379/pg10158-credloc-oracle-host-v1'
    assert not out.exists() and not slot.exists()
    def read(name,digest):
        return data.read_checked(data.BASE/name/'manifest.json',digest)
    pre = read('PG10156-credloc-preflight-v1','c0f8dfdfd40226b4ebd5d3e7c5083c3d191ef5bba8c67e4e1c1eeea329487259')
    host = read('PG10158-credloc-oracle-host-v1','76925993ffe20f5d5ba285adeb01f2a1996960203c1936d5cbe664ca84d99c44')
    normal = read('PG10154-credloc-six-compile-v1','683c715df260cde5a46f76888ad3e60159ddeae5e303e35992edc1edd9d0bf6e')
    old = read('PG10128-uid-oracle-six-compile-v1','7738e9ba61b5166e1ca9ed2223f6c7ce494051c9837526df1b2f549a0b7a92be')
    static = read('PG10152-credloc-precommit-static-v1','294e6388901717d9d2c5f9416644e800edd4ae7b23e670de893a01aef0421e1a')
    assert pre['source'] == host['source'] == normal['source'] == SOURCE
    assert pre['actualExit'] == host['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert host['begin']['permittedNativeScope'] == 'NONE' and not host['begin']['nativeAccessFlagAdded']
    cases = data.read_checked(data.BASE/'PG10156-credloc-preflight-v1/cases.json',pre['casesSha256'])
    expected = Counter((r['className'],r['method']) for r in cases)
    paths = sorted((run/'xml').glob('TEST-*.xml'))
    assert len(paths) == 1
    xml = ET.parse(paths[0]).getroot()
    assert xml.get('name') == BINARY and xml.get('tests') == '5'
    assert all(xml.get(k) == '0' for k in ('failures','errors','skipped'))
    actual = Counter((c.get('classname'),c.get('name')) for c in xml.findall('testcase'))
    assert actual == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert len(xml.findall('testcase')) == 5 and not any(list(c) for c in xml.findall('testcase'))
    assert not any(r['nonPass'] for r in host['cases']) and host['ownedTemporaryAfterEmpty']
    assert {paths[0].name:data.sha(paths[0].read_bytes())} == host['xmlHashes']
    assert (run/'xml/summary.safe.txt').read_text() == 'found=5;started=5;succeeded=5;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((run/'jacoco.exec').read_bytes()) == host['execSha256']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert static['sourceHashes'] == {TEST:hashes[TEST]} and static['baseSource'] == old['source']
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 2 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    assert {(v['rule'],int(v['beginline'])) for v in static['reports']['pmd']['details']} == {('DoNotUseThreads',66),('DoNotUseThreads',69)}
    deps = {**static['dependencyHashes'],**static['toolAndRuleHashes'],**host['begin']['dependencyHashes'],**pre['physicalTestFiles']}
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) == set(after) and len(after) == 1931
    selected = ('storage',BINARY.replace('.','/')+'.class')
    assert [k for k in after if after[k] != before[k]] == [selected]
    slot.mkdir(mode=0o700)
    subject = 'dev/codex/schubert/nk/storage/ServiceCredentialLocation.class'
    with zipfile.ZipFile(normal['jars']['storage']['path']) as archive:
        contents = archive.read(subject)
    assert pre['physicalMainClasses'] == {subject:data.sha(contents)}
    clazz = slot/'selected-main.class'
    with clazz.open('xb') as stream: stream.write(contents)
    helper = data.ROOT/'tools/quality/architecture/CredlocOracleCoverageMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = data.ROOT.parent/'toolchain'
    libs = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    library_hashes = {str(p):data.sha(p.read_bytes()) for p in libs}
    reader = slot/'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,libs))
    jdk = tc/'jdk-25.0.4/bin'
    steps.SLOT = slot
    stages = [steps.step('compile-reader',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('measure-saved-exec',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(run/'jacoco.exec'),str(clazz)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    text = (slot/'measure-saved-exec.stdout').read_text()
    lines = text.splitlines()
    assert len(lines) == 7 and lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
    session = parse(lines[0].split('\t'),'PG10158-CREDLOC-ORACLE')
    identity = lines[2].split('\t')
    assert identity[:2] == ['CLASS',subject.removesuffix('.class')] and len(identity) == 3
    counters = {}
    for line in lines[3:]:
        marker,kind,missed,covered = line.split('\t')
        assert marker == 'COUNTER' and kind not in counters
        counters[kind] = dict(missed=int(missed),covered=int(covered))
    applicability = classify(counters)
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in library_hashes.items())
    verify(invocation)
    out.mkdir()
    (out/paths[0].name).write_bytes(paths[0].read_bytes())
    (out/'coverage.txt').write_text(text)
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        helperSha256=helper_sha,libraryHashes=library_hashes,tests=5,suites=1,newTestIds=0,
        correctedExistingTestId='PT-OPS-CREDLOC-005',relatedRegressionMethods=4,session=session,
        execSha256=host['execSha256'],xmlHashes=host['xmlHashes'],classCrc64=identity[2],counters=counters,
        counterApplicability=applicability,four100=applicability=='FOUR100_MEASURED_APPLICABLE',
        coverageScope='COMPLETE_SERVICE_CREDENTIAL_LOCATION_SOURCE_ONE_PHYSICAL_CLASS',coverageUnion=False,
        forbiddenProductProbeHits=0,mainClassesByteIdentical=1843,otherTestClassesByteIdentical=1930,
        rawStaticExit=1,rawPmdFindings=2,checkstyleFindings=0,
        staticApplicability='two DoNotUseThreads JavaEE-context rules not applicable to standalone method-owned executor/TWR; raw1 preserved',
        suppressionsAdded=False,oldSourceBytesPreservedExceptDeclaredOracle=True,metadataSessionVectors=selftest(),
        productTestsReexecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=5,suites=1,counters=counters,four100=applicability=='FOUR100_MEASURED_APPLICABLE',
        manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
