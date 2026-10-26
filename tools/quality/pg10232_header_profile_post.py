"""PT125 XML/CRC and untouched native/other Test methods, with no product replay."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from class_counter_applicability import classify
from coverage_session_schema import parse as parse_session, selftest
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

ROOT = data.ROOT
BASE = data.BASE
SOURCE = 'ddde23ca0304654d59608b434c647c87d58ae3b6'
WORK = ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10230-header-profile-host-v1'
SLOT = WORK/'pg10232-header-profile-post-v1'
OUT = BASE/'PG10232-header-profile-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE/'PG10228-header-profile-preflight-v1/manifest.json',
        '3663b365873285f7c189397244c1386fb9ab4acd5d9e21c117449bfed7bd241c')
    host_sha = '8f82d84bd096d993e013dc6df6cc018782b8a9af9c7fde0b5e9e2e65b60fcc4f'
    host = data.read_checked(BASE/'PG10230-header-profile-host-v1/manifest.json',host_sha)
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    assert (prepared['expectedTests'],prepared['expectedSuites']) == (host['begin']['expectedTests'],host['begin']['expectedSuites']) == (1,1)
    cases = data.read_checked(BASE/'PG10228-header-profile-preflight-v1/cases.json',prepared['casesSha256'])
    expected = Counter((r['className'],r['method']) for r in cases)
    observed,xmls = [],{}
    for path in sorted((RUN/'xml').glob('TEST-*.xml')):
        tree = ET.parse(path).getroot()
        name = tree.get('name')
        assert name in prepared['caseCounts'] and int(tree.get('tests')) == prepared['caseCounts'][name]
        assert all(int(tree.get(k)) == 0 for k in ('failures','errors','skipped'))
        nodes = tree.findall('testcase')
        assert len(nodes) == prepared['caseCounts'][name] and all(n.get('classname') == name and not list(n) for n in nodes)
        observed.extend((n.get('classname'),n.get('name')) for n in nodes)
        xmls[path.name] = data.sha(path.read_bytes())
    assert len(xmls) == 1 and Counter(observed) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes'] and not any(r['nonPass'] for r in host['cases'])
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=1;started=1;succeeded=1;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(BASE/'PG10226-header-profile-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-codec'
    classes.mkdir()
    with zipfile.ZipFile(jar) as archive:
        for name,digest in prepared['physicalMainClasses'].items():
            assert name.startswith('dev/codex/schubert/nk/protocol/codec/HeaderCodec') and '..' not in Path(name).parts
            raw = archive.read(name)
            assert data.sha(raw) == digest
            target = classes/name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                stream.write(raw)
    assert len(prepared['physicalMainClasses']) == 1
    helper = ROOT/'tools/quality/architecture/HeaderProfileCoverageMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = ROOT.parent/'toolchain'
    libs = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    dependencies = {str(p):data.sha(p.read_bytes()) for p in libs}
    reader = SLOT/'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,libs))
    jdk = tc/'jdk-25.0.4/bin'
    steps.SLOT = SLOT
    stages = [steps.step('compile-report',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    selected_test = next(Path(p) for p in prepared['physicalTestFiles'] if p.endswith('/MessageCodecTest.class'))
    stages.append(steps.step('measure-complete-codec',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+cp,
        helper.stem,str(RUN/'jacoco.exec'),str(classes),str(selected_test)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    text = (SLOT/'measure-complete-codec.stdout').read_text()
    lines = text.splitlines()
    schema_vectors = selftest()
    session = parse_session(lines[0].split(chr(9)),'PG10230-HEADER-PROFILE')
    units = {}
    counters = None
    forbidden_hits = None
    test_methods = {}
    for line in lines[1:]:
        parts = line.split(chr(9))
        if parts[0] == 'FORBIDDEN_PROBE_HITS':
            assert parts == ['FORBIDDEN_PROBE_HITS','0'] and forbidden_hits is None
            forbidden_hits = 0
            continue
        if parts[0] == 'TEST_METHOD':
            assert len(parts) == 4 and parts[1] in prepared['allDeclaredTestMethods'] and parts[1] not in test_methods
            methods,instructions = map(int,parts[2:])
            if parts[1] == 'responseAndEventHeadersRoundTripWithoutLeakingContext': assert methods == 1 and instructions > 0
            else: assert methods == instructions == 0
            test_methods[parts[1]] = dict(coveredMethods=methods,coveredInstructions=instructions)
            continue
        if parts[0] == 'CLASS':
            assert len(parts) == 3 and parts[1]+'.class' in prepared['physicalMainClasses'] and parts[1] not in units
            counters = {}
            units[parts[1]] = dict(classCrc64=parts[2],counters=counters)
            continue
        kind,label,miss,hit = parts
        assert kind == 'COUNTER' and counters is not None and label not in counters
        counters[label] = dict(missed=int(miss),covered=int(hit))
    assert {k+'.class' for k in units} == set(prepared['physicalMainClasses']) and forbidden_hits == 0
    assert set(test_methods) == set(prepared['allDeclaredTestMethods']) and len(test_methods) == 7
    assert host['ownedTemporaryAfterEmpty'] and not list((RUN/'tmp').iterdir())
    for unit in units.values():
        unit['counterApplicability'] = classify(unit['counters'])
        unit['four100'] = unit['counterApplicability'] == 'FOUR100_MEASURED_APPLICABLE'
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    previous = data.read_checked(BASE/'PG10202-pre-sql-boundary-six-compile-v1/manifest.json',
        'a050b88ec51ec64a18d0abd5adf5ea2bf64304a496735acb40f4da8091dfa8f2')
    all_main,old_main = jar_classes(normal),jar_classes(previous)
    assert all_main == old_main and len(all_main) == 1843
    all_tests,old_tests = test_classes(normal),test_classes(previous)
    assert set(all_tests) == set(old_tests) and len(all_tests) == 1937
    changed_test = ('protocol','dev/codex/schubert/nk/protocol/codec/MessageCodecTest.class')
    assert {p for p,h in all_tests.items() if h != old_tests[p]} == {changed_test}
    static = data.read_checked(BASE/'PG10225-header-profile-static-v2/manifest.json',
        '3f6d9dbd16806f95e0e78cc65a525f2b8c7219cbcbef15f90e28215d34c85d58')
    assert static['actualExit'] == 0 and static['source'] is None and static['baseSource'] == previous['source']
    assert all(prepared['allCurrentSourceInputHashes'][p] == h for p,h in static['sourceHashes'].items())
    assert all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['toolAndRuleHashes'],**static['dependencyHashes']}.items())
    verify(invocation)
    OUT.mkdir()
    for path in (RUN/'xml').glob('TEST-*.xml'):
        (OUT/path.name).write_bytes(path.read_bytes())
    (OUT/'coverage.txt').write_text(text)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,hostManifestSha256=host_sha,stages=stages,
        tests=1,suites=1,newTestIds=0,xmlHashes=xmls,summaryTests=1,expectedTests=1,expectedSuites=1,
        session=session,sessionSchemaVectors=schema_vectors,execSha256=host['execSha256'],units=units,
        physicalMainClasses=prepared['physicalMainClasses'],
        targetUnitsFour100=all(u['four100'] for u in units.values()),forbiddenProductProbeHits=forbidden_hits,
        testMethodExecutionCounters=test_methods,
        onlyOneDeclaredTestMethodExecuted=True,ownedTemporaryAfterEmpty=True,
        mainClassesByteIdentical=len(all_main),otherSourceTestClassesByteIdentical=len(all_tests)-1,
        changedSourcePhysicalTestClasses=1,oldSourceTokensPreserved=prepared['allOriginalSourceTokensPreserved'],
        staticRawExit=0,pmdFindings=0,checkstyleFindings=0,staticSourceHashBound=True,
        helperSha256=helper_sha,libraryHashes=dependencies,
        coverageScope='COMPLETE_HEADER_CODEC_SOURCE_ONE_PHYSICAL_CLASS_LIMITED_HEADER_METHOD_ONLY',whole451Accepted=False,
        correctedExistingTestIds=['PT-PRO-002-H01'],nativeCohortQualified=False,
        historicalSuccessTransferred=False,coverageUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=1,suites=1,units=units,targetUnitsFour100=result['targetUnitsFour100'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
