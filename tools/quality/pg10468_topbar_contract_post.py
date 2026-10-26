"""Read original28-method boundary results and complete selected class counters, no PT replay."""
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

SOURCE = '73c18457afce837ecfc3687fc7aae84c04cca2c1'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10466-topbar-contract-host-v1'
SLOT = WORK/'pg10468-topbar-contract-post-v1'
OUT = data.BASE/'PG10468-topbar-contract-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(data.BASE/'PG10464-topbar-contract-preflight-v1/manifest.json',
        'e2d192b538ab00a5017ea9f61155d4135e40cdc370258fa4861fcbbfbf43e7bc')
    host = data.read_checked(data.BASE/'PG10466-topbar-contract-host-v1/manifest.json',
        'eddee6d07e419fc3dc3fc5b4c24d3f9ef53d100af85f84e36c276e20eaafac74')
    normal = data.read_checked(data.BASE/'PG10462-topbar-contract-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    assert prepared['actualExit'] == host['actualExit'] == normal['actualExit'] == 0
    assert prepared['source'] == host['source'] == normal['source'] == SOURCE and normal['testsExecuted'] == 0
    cases = data.read_checked(data.BASE/'PG10464-topbar-contract-preflight-v1/cases.json',prepared['casesSha256'])
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
    assert len(xmls) == 3 and Counter(actual) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes'] and not any(r['nonPass'] for r in host['cases'])
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=28;started=28;succeeded=28;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert host['newTestIds'] == 0 and host['existingChangedMethods'] == 28
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
            assert name.startswith('dev/codex/schubert/nk/web/view/') and '..' not in Path(name).parts
            raw = archive.read(name)
            assert data.sha(raw) == digest
            path = classes/name
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream: stream.write(raw)
    helper = data.ROOT/'tools/quality/architecture/RoleLiteralViewCoverageMeasure10466.java'
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
    session = parse_session(lines[0].split(chr(9)),'PG10466-TOPBAR-CONTRACT')
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
    assert {n+'.class' for n in units} == set(prepared['physicalMainClasses']) and len(units) == 15
    for unit in units.values(): unit['counterApplicability'] = classify(unit['counters'])
    previous = data.read_checked(data.BASE/'PG10434-pure-view-six-compile-v1/manifest.json',
        'd202203f8377e778f1c8b43af42cbad0e8a97614cb0b82e7e97b3143652b5f7e')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before_test,after_test = test_classes(previous),test_classes(normal)
    physical_changes = {}
    for module,name in set(before_test)|set(after_test):
        if before_test.get((module,name)) == after_test.get((module,name)): continue
        source_normal = normal if (module,name) in after_test else previous
        path = Path(source_normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(path.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in prepared['changedTestSourceHashes']}
        physical_changes[module+':'+name] = dict(sourceFile=model['sourceFile'],
            beforeSha256=before_test.get((module,name)),sha256=after_test.get((module,name)))
    static = data.read_checked(data.BASE/'PG10460-topbar-contract-static-v1/manifest.json',
        'fe30b85e0e7c678bf7b7352c830bcf31218bf1506ccc9a0a53c5c10eaa2a72ec')
    assert static['sourceHashes'] == prepared['changedTestSourceHashes'] and static['actualExit'] == 1
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    verify(invocation)
    OUT.mkdir()
    public_xml = OUT/'xml'
    public_xml.mkdir()
    for path in sorted((RUN/'xml').iterdir()):
        assert path.is_file() and (path.name in xmls or path.name == 'summary.safe.txt')
        with (public_xml/path.name).open('xb') as stream: stream.write(path.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        originalHostManifestSha256='eddee6d07e419fc3dc3fc5b4c24d3f9ef53d100af85f84e36c276e20eaafac74',
        tests=28,suites=3,newTestIds=0,xmlHashes=xmls,sourceHashes=prepared['changedTestSourceHashes'],
        jacocoSession=session,sessionSchemaMetadataVectors=schema_vectors,coverageByCompleteSelectedClass=units,
        coverageMeasuredSelectedFifteenOnly=True,wholeJavaCoverage100=False,oldExecUnion=False,
        heldProbeHits=0,prohibitedLoadedClasses=hits,loadedClassMetadataSha256=data.sha((RUN/'classload-metadata.log').read_bytes()),
        coverageReaderSha256=helper_sha,coverageReaderDependencies=dependencies,
        mainClassesUnchanged=1843,physicalTestChanges=physical_changes,
        otherTestClassesUnchanged=sum(before_test.get(k) == h for k,h in after_test.items()),
        testClassesBefore=len(before_test),testClassesAfter=len(after_test),
        rawStaticExit=1,rawPmdFindings=6,checkstyleFindings=0,pmdApplicabilityComplete=True,contextuallyApplicableFindings=0,
        wholeF03Accepted=False,wholeG03Accepted=False,whole451Accepted=False,actualExternalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=28,suites=3,units=len(units),physicalTestChanges=len(physical_changes),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
