"""Read original14-method public template results and complete selected class counters, no PT replay."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
from class_counter_applicability import classify
from classfile_code_metadata import decode
from coverage_session_schema import parse as parse_session, selftest
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10488-public-template-host-v1'
SLOT = WORK/'pg10490-public-template-post-v1'
OUT = data.BASE/'PG10490-public-template-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(data.BASE/'PG10486-public-template-preflight-v1/manifest.json',
        '781f1048b32a310e8d5b961116c5e5268e33e3625d4e472ce3dd23e9979666d4')
    host = data.read_checked(data.BASE/'PG10488-public-template-host-v1/manifest.json',
        '5c3d39c1dc47bfeff143406b8955818165d79a865097fe35e5cf473f114f8dbe')
    normal = data.read_checked(data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json',prepared['normalManifestSha256'])
    assert prepared['actualExit'] == host['actualExit'] == normal['actualExit'] == 0
    assert prepared['source'] == host['source'] == normal['source'] == SOURCE and normal['testsExecuted'] == 0
    cases = data.read_checked(data.BASE/'PG10486-public-template-preflight-v1/cases.json',prepared['casesSha256'])
    source_proof = data.read_checked(data.BASE/'PG10482-disjoint-six-literal-post-v1/manifest.json',prepared['sourceProofManifestSha256'])
    assert source_proof['actualExit'] == 0 and source_proof['source'] == SOURCE
    expected = Counter((r['className'],r['method']) for r in cases)
    actual,xmls = [],{}
    for p in sorted((RUN/'xml').glob('TEST-*.xml')):
        root = ET.parse(p).getroot()
        name = root.get('name')
        assert name in prepared['caseCounts'] and int(root.get('tests')) == prepared['caseCounts'][name]
        assert all(int(root.get(k)) == 0 for k in ('failures','errors','skipped'))
        assert all(not list(c) for c in root.findall('testcase'))
        actual.extend((c.get('classname'),c.get('name')) for c in root.findall('testcase'))
        xmls[p.name] = data.sha(p.read_bytes())
    assert len(xmls) == 2 and Counter(actual) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes'] and not any(r['nonPass'] for r in host['cases'])
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=14;started=14;succeeded=14;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert host['newTestIds'] == 0 and host['existingChangedMethods'] == 14
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    loaded_text = (RUN/'classload-metadata.log').read_text()
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loaded_text))
    prohibited = ('dev.codex.schubert.nk.api.','dev.codex.schubert.nk.batch.',
        'dev.codex.schubert.nk.bootstrap.','dev.codex.schubert.nk.storage.',
        'dev.codex.schubert.nk.web.bootstrap.','dev.codex.schubert.nk.web.logging.',
        'dev.codex.schubert.nk.web.transport.','dev.codex.schubert.nk.web.session.JdbcWebSessionStore','org.postgresql.')
    hits = sorted(n for n in loaded if n.startswith(prohibited))
    assert loaded and not hits
    assert all(p.removesuffix('.class').replace('/','.') in loaded for p in prepared['physicalMainClasses'])
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-main'
    classes.mkdir()
    with zipfile.ZipFile(normal['jars']['web']['path']) as archive:
        for name,digest in prepared['physicalMainClasses'].items():
            assert name.startswith('dev/codex/schubert/nk/web/') and '..' not in Path(name).parts
            raw = archive.read(name)
            assert data.sha(raw) == digest
            path = classes/name
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream: stream.write(raw)
    helper = data.ROOT/'tools/quality/architecture/PublicTemplate14CoverageMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = data.ROOT.parent/'toolchain'
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
    stages.append(steps.step('measure-main',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    lines = (SLOT/'measure-main.stdout').read_text().splitlines()
    schema_vectors = selftest()
    session = parse_session(lines[0].split(chr(9)),'PG10488-PUBLIC-TEMPLATE14')
    assert lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
    units,current = {},None
    for line in lines[2:]:
        parts = line.split(chr(9))
        if parts[0] == 'CLASS':
            assert len(parts) == 3 and parts[1]+'.class' in prepared['physicalMainClasses'] and parts[1] not in units
            current = dict(classCrc64=parts[2],counters={})
            units[parts[1]] = current
        else:
            kind,label,miss,hit = parts
            assert kind == 'COUNTER' and current is not None and label not in current['counters']
            current['counters'][label] = dict(missed=int(miss),covered=int(hit))
    assert {n+'.class' for n in units} == set(prepared['physicalMainClasses']) and len(units) == 14
    for unit in units.values(): unit['counterApplicability'] = classify(unit['counters'])
    previous = data.read_checked(data.BASE/'PG10462-topbar-contract-six-compile-v1/manifest.json',
        '1b73c7462722d9a221a56daad3cb9d9efcbbee6a4385926d0ea9c379bec7d15b')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before_test,after_test = test_classes(previous),test_classes(normal)
    physical_changes = {}
    for module,name in set(before_test)|set(after_test):
        if before_test.get((module,name)) == after_test.get((module,name)): continue
        source_normal = normal if (module,name) in after_test else previous
        path = Path(source_normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(path.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in source_proof['sourceHashes']}
        physical_changes[module+':'+name] = dict(sourceFile=model['sourceFile'],
            beforeSha256=before_test.get((module,name)),sha256=after_test.get((module,name)))
    static = data.read_checked(data.BASE/'PG10478-disjoint-six-literal-static-v1/manifest.json',
        '1cae3c256e3442adace66f78b521f981b119754d1edfeaef03ac0c2a4f73e4bc')
    assert all(static['sourceHashes'].get(p) == h for p,h in prepared['changedTestSourceHashes'].items()) and static['actualExit'] == 1
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    verify(invocation)
    OUT.mkdir()
    public_xml = OUT/'xml'
    public_xml.mkdir()
    for path in sorted((RUN/'xml').iterdir()):
        assert path.is_file() and (path.name in xmls or path.name == 'summary.safe.txt')
        with (public_xml/path.name).open('xb') as stream: stream.write(path.read_bytes())
    traces = {}
    expected_traces = {
        'PT-SCR-053.txt': 'templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n',
        'PT-SCR-071.txt': 'templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n'}
    trace_root = Path(prepared['publicTraceDirectory'])
    assert trace_root == Path(host['normalTemplateModulePath'])/'target/scenario-screen-traces'
    assert sorted(p.name for p in trace_root.iterdir()) == prepared['expectedPublicTraceFileNames']
    public_traces = OUT/'public-count-traces'
    public_traces.mkdir()
    for name,text in expected_traces.items():
        path = trace_root/name
        assert path.is_file() and not path.is_symlink() and path.read_bytes() == text.encode('ascii')
        traces[name] = data.sha(path.read_bytes())
        assert traces[name] == host['publicTraceHashes'][name]
        with (public_traces/name).open('xb') as stream:
            stream.write(path.read_bytes())
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((Path(host['normalTemplateModulePath']).parents[1]/p).read_bytes()) == h for p,h in prepared['publicResourceHashes'].items())
    data.write(OUT/'manifest.json' ,dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        originalHostManifestSha256='5c3d39c1dc47bfeff143406b8955818165d79a865097fe35e5cf473f114f8dbe',
        tests=14,suites=2,newTestIds=0,publicCountTraceHashes=traces,rawHtmlOrCsrfPublished=False,
        physicalSourceChangeScope=list(source_proof['sourceHashes']),selectedRuntimeSourceCount=2,xmlHashes=xmls,sourceHashes=prepared['changedTestSourceHashes'],
        jacocoSession=session,sessionSchemaMetadataVectors=schema_vectors,coverageByCompleteSelectedClass=units,
        coverageMeasuredSelectedFourteenOnly=True,wholeJavaCoverage100=False,oldExecUnion=False,
        heldProbeHits=0,prohibitedLoadedClasses=hits,loadedClassMetadataSha256=data.sha((RUN/'classload-metadata.log').read_bytes()),
        coverageReaderSha256=helper_sha,coverageReaderDependencies=dependencies,
        mainClassesUnchanged=1843,physicalTestChanges=physical_changes,
        otherTestClassesUnchanged=sum(before_test.get(k) == h for k,h in after_test.items()),
        testClassesBefore=len(before_test),testClassesAfter=len(after_test),
        rawStaticExit=1,rawPmdFindings=26,checkstyleFindings=0,pmdApplicabilityComplete=False,contextuallyApplicableFindings=None,pendingOtherSourceApplicability=10,
        wholeF03Accepted=False,wholeG03Accepted=False,whole451Accepted=False,actualExternalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=14,suites=2,units=len(units),physicalTestChanges=len(physical_changes),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
