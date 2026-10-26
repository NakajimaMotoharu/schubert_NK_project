"""Original twenty-two XML plus no-SQL/held probes, complete Main counters and static join."""
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
SOURCE = 'f12718441140c670950760185b596ab5627377db'
WORK = ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10264-scenario-media-boundary-host-v1'
SLOT = WORK/'pg10266-scenario-media-boundary-post-v1'
OUT = BASE/'PG10266-scenario-media-boundary-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE/'PG10262-scenario-media-boundary-preflight-v1/manifest.json',
        'b754c6de3bf345c52acbc1788ee66bc05ae5deb6956a721b610968097f4faf72')
    host_sha = '7644b073f2e2678ff7ea8971a944473e0476a2c9fee6dc397578e782ef66a031'
    host = data.read_checked(BASE/'PG10264-scenario-media-boundary-host-v1/manifest.json',host_sha)
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    assert (prepared['expectedTests'],prepared['expectedSuites']) == (host['begin']['expectedTests'],host['begin']['expectedSuites']) == (22,2)
    cases = data.read_checked(BASE/'PG10262-scenario-media-boundary-preflight-v1/cases.json',prepared['casesSha256'])
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
    assert len(xmls) == 2 and Counter(observed) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes'] and not any(r['nonPass'] for r in host['cases'])
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=22;started=22;succeeded=22;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(BASE/'PG10263-scenario-media-six-compile-v2/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-codec'
    classes.mkdir()
    with zipfile.ZipFile(jar) as archive:
        for name,digest in prepared['physicalMainClasses'].items():
            assert name.startswith('dev/codex/schubert/nk/api/') and '..' not in Path(name).parts
            raw = archive.read(name)
            assert data.sha(raw) == digest
            target = classes/name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                stream.write(raw)
    assert len(prepared['physicalMainClasses']) == 4
    helper = ROOT/'tools/quality/architecture/ScenarioMediaBoundaryCoverageMeasure.java'
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
    test_root = WORK/'pg10263-scenario-media-six-compile-v2/snapshot/src/schubert-nk-api/target/test-classes'
    stages.append(steps.step('measure-complete-codec',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(test_root)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    text = (SLOT/'measure-complete-codec.stdout').read_text()
    lines = text.splitlines()
    schema_vectors = selftest()
    session = parse_session(lines[0].split(chr(9)),'PG10264-SCENARIO-MEDIA-BOUNDARY')
    units = {}
    counters = None
    forbidden_hits = None
    sql_hits = jdbc_hits = None
    for line in lines[1:]:
        parts = line.split(chr(9))
        if parts[0] == 'SQL_HELPER_HITS':
            assert parts == ['SQL_HELPER_HITS','0'] and sql_hits is None
            sql_hits = 0
            continue
        if parts[0] == 'JDBC_GUARD_HITS':
            assert parts == ['JDBC_GUARD_HITS','0','2'] and jdbc_hits is None
            jdbc_hits = 0
            continue
        if parts[0] == 'FORBIDDEN_PROBE_HITS':
            assert parts == ['FORBIDDEN_PROBE_HITS','0'] and forbidden_hits is None
            forbidden_hits = 0
            continue
        if parts[0] == 'CLASS':
            assert len(parts) == 3 and parts[1]+'.class' in prepared['physicalMainClasses'] and parts[1] not in units
            counters = {}
            units[parts[1]] = dict(classCrc64=parts[2],counters=counters)
            continue
        kind,label,miss,hit = parts
        assert kind == 'COUNTER' and counters is not None and label not in counters
        counters[label] = dict(missed=int(miss),covered=int(hit))
    assert {k+'.class' for k in units} == set(prepared['physicalMainClasses']) and forbidden_hits == sql_hits == jdbc_hits == 0
    for unit in units.values():
        unit['counterApplicability'] = classify(unit['counters'])
        unit['four100'] = unit['counterApplicability'] == 'FOUR100_MEASURED_APPLICABLE'
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    previous = data.read_checked(BASE/'PG10226-header-profile-six-compile-v1/manifest.json',
        'ffb1b71ad14efa4b8921c58a19541728243e35d60f873983528bce177b914b9c')
    main_now,main_old = jar_classes(normal),jar_classes(previous)
    assert main_now == main_old and len(main_now) == 1843
    test_now,test_old = test_classes(normal),test_classes(previous)
    assert len(test_old) == 1937 and len(test_now) == 1941
    assert all(test_now[p] == h for p,h in test_old.items())
    expected_added = {('api',r['className'].replace('.','/')+suffix+'.class') for r in cases for suffix in ('','$NoSql')}
    assert set(test_now)-set(test_old) == expected_added and len(expected_added) == 4
    static = data.read_checked(BASE/'PG10261-scenario-media-boundary-static-v3/manifest.json',
        '1caa334d9d8cc396c5639395c4980ba3f78a972bd515a7eee4413ba781e84741')
    assert static['source'] is None and static['actualExit'] == 1
    assert static['sourceHashes'] == prepared['newSourceHashes']
    assert static['reports']['pmd']['findings'] == 4 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    static_xml = BASE/'PG10261-scenario-media-boundary-static-v3/pmd.xml'
    assert data.sha(static_xml.read_bytes()) == static['reports']['pmd']['sha256']
    applicability = []
    for file in ET.parse(static_xml).getroot().iter():
        if file.tag.rsplit('}',1)[-1] != 'file': continue
        for item in file:
            rule = item.get('rule')
            assert rule in ('CloseResource','UseProperClassLoader')
            applicability.append(dict(file=file.get('name'),line=int(item.get('beginline')),rule=rule,
                status='NON_APPLICABLE_CONTEXT',reason=('JDK synthetic Proxy; no actual connection opened; any invocation including close is forbidden'
                if rule == 'CloseResource' else 'Standalone JUnit JDK public Connection interface proxy, not JavaEE classloader ownership')))
    assert Counter(r['rule'] for r in applicability) == {'CloseResource':2,'UseProperClassLoader':2}
    assert host['newTestIds'] == len(cases) == len({r['testId'] for r in cases}) == 22
    verify(invocation)
    OUT.mkdir()
    for path in (RUN/'xml').glob('TEST-*.xml'):
        (OUT/path.name).write_bytes(path.read_bytes())
    (OUT/'coverage.txt').write_text(text)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,hostManifestSha256=host_sha,stages=stages,
        tests=22,suites=2,newTestIds=len(cases),xmlHashes=xmls,summaryTests=22,expectedTests=22,expectedSuites=2,
        session=session,sessionSchemaVectors=schema_vectors,execSha256=host['execSha256'],units=units,
        physicalMainClasses=prepared['physicalMainClasses'],
        targetUnitsFour100=all(u['four100'] for u in units.values()),forbiddenProductProbeHits=forbidden_hits,
        sqlHelperCoveredInstructions=sql_hits,jdbcGuardCoveredInstructions=jdbc_hits,jdbcGuardCount=2,
        mainClassesByteIdentical=len(main_now),previousTestClassesByteIdentical=len(test_old),newPhysicalTestClasses=len(expected_added),
        staticRawExit=1,staticFindings=applicability,applicableStaticViolations=0,staticSuppressionsAdded=0,
        helperSha256=helper_sha,libraryHashes=dependencies,
        coverageScope='COMPLETE_SCENARIO_MEDIA_REPOSITORIES_TWO_NO_CODE_INTERFACES_SINGLE_PRE_SQL_RUN',whole451Accepted=False,
        historicalSuccessTransferred=False,coverageUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=22,suites=2,units=units,targetUnitsFour100=result['targetUnitsFour100'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
