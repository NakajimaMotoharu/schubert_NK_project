"""Independent entire protocol module XML/session/CRC/counter post, no product rerun."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
RUN = WORK / 'pg9722-protocol-module-host-v1'
SLOT = WORK / 'pg9724-protocol-module-post-v1'
OUT = BASE / 'PG9724-protocol-module-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE / 'PG9720-protocol-module-preflight-v1/manifest.json',
        '97b3f79828efef6b07a49de2505d1a6fc8f07520b714acdfb6aadf01f51855a3')
    host = data.read_checked(RUN / 'manifest.safe.json','ddcc4a3ae1644a15b61365e645af41e26e4d255d936be1ed008ce42a87d80692')
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    cases = data.read_checked(BASE / 'PG9720-protocol-module-preflight-v1/cases.json',prepared['casesSha256'])
    assert len(host['stages']) == 2 and all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert len(host['cases']) == 102 and not any(r['nonPass'] for r in host['cases'])
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
    assert len(xmls) == 22 and Counter(actual) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes']
    summary = RUN / 'xml/summary.safe.txt'
    assert summary.read_text() == 'found=102;started=102;succeeded=102;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    assert data.sha((RUN / 'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT / 'complete-module'
    classes.mkdir()
    selected = {}
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if name.endswith('.class'):
                assert name.startswith('dev/codex/schubert/nk/protocol/') and '..' not in Path(name).parts
                content = archive.read(name)
                target = classes / name
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(content)
                selected[name[:-6]] = data.sha(content)
    assert len(selected) == 176 and {n + '.class':h for n,h in selected.items()} == prepared['physicalMainClasses']
    catalog = SLOT / 'all-physical-classes.txt'
    with catalog.open('x') as stream:
        stream.write('\n'.join(sorted(selected)) + '\n')
    helper = ROOT / 'tools/quality/architecture/ProtocolModuleCoverageMeasure.java'
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
    session = lines[0].split('\t')
    assert session[:2] == ['SESSION','PG9722-PROTOCOL-FULL-MODULE'] and int(session[2]) <= int(session[3])
    measured = {}
    misses = []
    for line in lines[1:]:
        parts = line.split('\t')
        if parts[0] == 'CLASS':
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
    assert set(measured) == set(selected) and all(set(v['counters']) == {'LINE','METHOD','CLASS','BRANCH'} for v in measured.values())
    aggregate = {kind:{field:sum(v['counters'][kind][field] for v in measured.values()) for field in ('missed','covered')} for kind in ('LINE','METHOD','CLASS','BRANCH')}
    complete = sorted(n for n,v in measured.items() if all(c['missed'] == 0 for c in v['counters'].values()))
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
    data.write(OUT / 'whole-module-counters.json',dict(physicalClasses=measured,missedMethods=misses))
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,actualTests=102,suites=22,newTestIds=0,
        hostManifestSha256='ddcc4a3ae1644a15b61365e645af41e26e4d255d936be1ed008ce42a87d80692',
        preflightManifestSha256='97b3f79828efef6b07a49de2505d1a6fc8f07520b714acdfb6aadf01f51855a3',
        xmlHashes=xmls,summarySha256=data.sha(summary.read_bytes()),execSha256=host['execSha256'],sessionId=session[1],
        sessionStartMillis=int(session[2]),sessionEndMillis=int(session[3]),physicalMainClassCount=176,
        wholeModuleCounters=aggregate,wholeModuleFour100=all(c['missed'] == 0 for c in aggregate.values()),
        physicalClassHashes=selected,four100PhysicalClassCount=len(complete),nonExecutableMetadataClasses=no_code,
        moduleCounterDetailsSha256=data.sha((OUT / 'whole-module-counters.json').read_bytes()),
        reportHelperSha256=helper_sha,reportLibraryHashes=deps,reportStages=stages,
        failed=0,errors=0,skipped=0,aborted=0,productTestsExecutedByPost=0,coverageUnion=False,exclusionsAdded=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,programPtComplete=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=102,physicalClasses=176,four100Classes=len(complete),wholeModuleCounters=aggregate,
        wholeModuleFour100=result['wholeModuleFour100'],manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
