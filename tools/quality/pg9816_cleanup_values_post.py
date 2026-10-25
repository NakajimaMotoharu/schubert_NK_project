"""Independent four-source-unit cleanup XML/session/CRC/counter post, no product rerun."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from class_counter_applicability import classify
from coverage_session_schema import parse as parse_session, selftest as session_selftest
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
RUN = WORK / 'pg9814-cleanup-values-host-v2'
SLOT = WORK / 'pg9816-cleanup-values-post-v1'
OUT = BASE / 'PG9816-cleanup-values-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE / 'PG9813-cleanup-values-preflight-v1/manifest.json',
        '5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344')
    host = data.read_checked(RUN / 'manifest.safe.json','3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944')
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    cases = data.read_checked(BASE / 'PG9813-cleanup-values-preflight-v1/cases.json',prepared['casesSha256'])
    assert len(host['stages']) == 2 and all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert len(host['cases']) == 4 and not any(r['nonPass'] for r in host['cases'])
    expected = Counter((r['className'],r['method']) for r in cases)
    actual = []
    xmls = {}
    for path in sorted((RUN / 'xml').glob('TEST-*.xml')):
        root = ET.parse(path).getroot()
        name = root.get('name')
        assert name in prepared['caseCounts'] and int(root.get('tests')) == prepared['caseCounts'][name]
        assert all(int(root.get(k)) == 0 for k in ('failures','errors','skipped'))
        nodes = root.findall('testcase')
        assert len(nodes) == prepared['caseCounts'][name] and all(n.get('classname') == name and not list(n) for n in nodes)
        actual.extend((n.get('classname'),n.get('name')) for n in nodes)
        xmls[path.name] = data.sha(path.read_bytes())
    assert len(xmls) == 1 and Counter(actual) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes']
    summary = RUN / 'xml/summary.safe.txt'
    assert summary.read_text() == 'found=4;started=4;succeeded=4;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    assert data.sha((RUN / 'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['batch']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['batch']['sha256']
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT / 'complete-module'
    classes.mkdir()
    selected = {}
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if name in prepared['physicalMainClasses']:
                assert name.startswith('dev/codex/schubert/nk/batch/') and '..' not in Path(name).parts
                content = archive.read(name)
                target = classes / name
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(content)
                selected[name[:-6]] = data.sha(content)
    assert len(selected) == 4 and {n + '.class':h for n,h in selected.items()} == prepared['physicalMainClasses']
    catalog = SLOT / 'all-physical-classes.txt'
    with catalog.open('x') as stream:
        stream.write('\n'.join(sorted(selected)) + '\n')
    helper = ROOT / 'tools/quality/architecture/CleanupValueCoverageMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = ROOT.parent / 'toolchain'
    libraries = [tc / 'm2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc / f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    deps = {str(p):data.sha(p.read_bytes()) for p in libraries}
    cp = os.pathsep.join(map(str,libraries))
    reader = SLOT / 'reader'
    reader.mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-report',[str(tc / 'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('measure-complete-module',[str(tc / 'jdk-25.0.4/bin/java'),'-cp',str(reader) + os.pathsep + cp,helper.stem,str(RUN / 'jacoco.exec'),str(classes),str(catalog)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    lines = (SLOT / 'measure-complete-module.stdout').read_text().splitlines()
    schema_vectors = session_selftest()
    session = parse_session(lines[0].split(chr(9)),'PG9814-CLEANUP-VALUES')
    measured = {}
    structural_no_code = {}
    selftest = 0
    misses = []
    for line in lines[1:]:
        parts = line.split('\t')
        if parts[0] == 'TOOL_SELFTEST':
            assert parts == ['TOOL_SELFTEST','6'] and selftest == 0
            selftest = 6
        elif parts[0] == 'NO_CODE':
            _,name,kind,fields,methods = parts
            assert name in selected and name not in structural_no_code and kind in {'PACKAGE_ANNOTATION','NO_CODE_INTERFACE'}
            assert kind != 'PACKAGE_ANNOTATION' or (name.endswith('/package-info') and int(fields) == int(methods) == 0)
            structural_no_code[name] = dict(kind=kind,fields=int(fields),methods=int(methods),codeMethods=0,classfileSha256=selected[name])
        elif parts[0] == 'CLASS':
            _,name,crc,has_data = parts
            assert name in selected and name not in measured
            measured[name] = dict(crc64=crc,executionDataPresent=has_data == 'true',counters={})
        elif parts[0] == 'COUNTER':
            _,name,kind,missed,covered = parts
            assert kind not in measured[name]['counters']
            measured[name]['counters'][kind] = dict(missed=int(missed),covered=int(covered))
        else:
            assert parts[0] == 'MISS_METHOD'
            _,name,method,descriptor,ml,cl,mb,cb = parts
            misses.append(dict(className=name,method=method,descriptor=descriptor,missedLine=int(ml),coveredLine=int(cl),missedBranch=int(mb),coveredBranch=int(cb)))
    assert set(measured) <= set(selected) and set(measured) | set(structural_no_code) == set(selected)
    assert selftest == 6 and all(set(v['counters']) == {'LINE','METHOD','CLASS','BRANCH'} for v in measured.values())
    assert {n for n,v in structural_no_code.items() if v['kind'] == 'PACKAGE_ANNOTATION'} == {n for n in selected if n.endswith('/package-info')}
    assert len(structural_no_code) == 0 and all(v['kind'] == 'NO_CODE_INTERFACE' and v['fields'] == 0 for v in structural_no_code.values())
    aggregate = {kind:{field:sum(v['counters'][kind][field] for v in measured.values()) for field in ('missed','covered')} for kind in ('LINE','METHOD','CLASS','BRANCH')}
    complete = sorted(n for n,v in measured.items() if classify(v['counters']) == 'FOUR100_MEASURED_APPLICABLE')
    no_code = sorted(n for n,v in measured.items() if all(c['missed'] + c['covered'] == 0 for c in v['counters'].values()))
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    assert all(data.sha((classes / (n + '.class')).read_bytes()) == h for n,h in selected.items())
    verify(invocation)
    OUT.mkdir()
    for name in xmls:
        with (OUT / name).open('xb') as stream:
            stream.write((RUN / 'xml' / name).read_bytes())
    with (OUT / 'summary.safe.txt').open('xb') as stream:
        stream.write(summary.read_bytes())
    data.write(OUT / 'subject-unit-counters.json',dict(physicalClasses=measured,structuralNoCodeClasses=structural_no_code,missedMethods=misses))
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,actualTests=4,suites=1,newTestIds=4,
        hostManifestSha256='3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944',
        preflightManifestSha256='5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344',
        xmlHashes=xmls,summarySha256=data.sha(summary.read_bytes()),execSha256=host['execSha256'],sessionId=session['sessionId'],
        sessionStartMillis=session['startMillis'],sessionEndMillis=session['endMillis'],physicalMainClassCount=4,
        selectedSourceUnitCounters=aggregate,selectedSourceUnitFour100=all(c['missed'] == 0 for c in aggregate.values()),
        wholeBatchModuleQualified=False,counterApplicabilityHelperSha256=data.sha((ROOT / 'tools/quality/class_counter_applicability.py').read_bytes()),
        physicalClassHashes=selected,four100ExecutableClassCount=len(complete),nonExecutableMetadataClasses=no_code,
        structuralNoCodeClasses=structural_no_code,coverageReportedClassCount=len(measured),allPhysicalClassInventoryIncluded=True,
        zeroCountersNotArtificiallyCreated=True,metadataVectors=selftest,
        moduleCounterDetailsSha256=data.sha((OUT / 'subject-unit-counters.json').read_bytes()),
        reportHelperSha256=helper_sha,reportLibraryHashes=deps,reportStages=stages,sessionSchemaVectors=schema_vectors,
        sessionSchemaHelperSha256=data.sha((ROOT / 'tools/quality/coverage_session_schema.py').read_bytes()),
        failed=0,errors=0,skipped=0,aborted=0,productTestsExecutedByPost=0,coverageUnion=False,exclusionsAdded=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,programPtComplete=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=4,physicalClasses=4,four100Classes=len(complete),selectedSourceUnitCounters=aggregate,
        selectedSourceUnitFour100=result['selectedSourceUnitFour100'],manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
