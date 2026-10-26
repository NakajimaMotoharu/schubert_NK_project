"""Question/notice XML, same-source CRC and all three physical classes; empty interface not 100."""
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

ROOT = data.ROOT
BASE = data.BASE
SOURCE = 'dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77'
WORK = ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10104-query-batch-host-v1'
SLOT = WORK/'pg10106-query-batch-post-v1'
OUT = BASE/'PG10106-query-batch-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE/'PG10102-query-batch-preflight-v1/manifest.json',
        '28acacaad47d55acfbb698a206d79cb4d6d6e04a30fa332709b9ae0fd5fe2b19')
    host_sha = '1636ab4dbc7822ded2675cda9820b5af1bec40f091bbdf717f9c0e301f79ac9a'
    host = data.read_checked(BASE/'PG10104-query-batch-host-v1/manifest.json',host_sha)
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    assert (prepared['expectedTests'],prepared['expectedSuites']) == (host['begin']['expectedTests'],host['begin']['expectedSuites']) == (52,7)
    cases = data.read_checked(BASE/'PG10102-query-batch-preflight-v1/cases.json',prepared['casesSha256'])
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
    assert len(xmls) == 7 and Counter(observed) == expected == Counter((r['classname'],r['name']) for r in host['cases'])
    assert xmls == host['xmlHashes'] and not any(r['nonPass'] for r in host['cases'])
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=52;started=52;succeeded=52;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(BASE/'PG10100-query-batch-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
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
    assert len(prepared['physicalMainClasses']) == 7
    helper = ROOT/'tools/quality/architecture/QueryValidProjectionCoverageMeasure.java'
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
    stages.append(steps.step('measure-complete-codec',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    text = (SLOT/'measure-complete-codec.stdout').read_text()
    lines = text.splitlines()
    schema_vectors = selftest()
    session = parse_session(lines[0].split(chr(9)),'PG10104-QUERY-VALID-PROJECTION')
    units = {}
    counters = None
    forbidden_hits = None
    for line in lines[1:]:
        parts = line.split(chr(9))
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
    assert {k+'.class' for k in units} == set(prepared['physicalMainClasses']) and forbidden_hits == 0
    for unit in units.values():
        unit['counterApplicability'] = classify(unit['counters'])
        unit['four100'] = unit['counterApplicability'] == 'FOUR100_MEASURED_APPLICABLE'
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    for path in (RUN/'xml').glob('TEST-*.xml'):
        (OUT/path.name).write_bytes(path.read_bytes())
    (OUT/'coverage.txt').write_text(text)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,hostManifestSha256=host_sha,stages=stages,
        tests=52,suites=7,newTestIds=4,xmlHashes=xmls,summaryTests=52,expectedTests=52,expectedSuites=7,
        session=session,sessionSchemaVectors=schema_vectors,execSha256=host['execSha256'],units=units,
        physicalMainClasses=prepared['physicalMainClasses'],
        targetUnitsFour100=all(u['four100'] for u in units.values()),forbiddenProductProbeHits=forbidden_hits,
        questionRequestFour100=units['dev/codex/schubert/nk/api/application/question/QuestionQueryRequest']['four100'],
        requestUnitsFour100={name:unit['four100'] for name,unit in units.items() if name.endswith('Request')},
        helperSha256=helper_sha,libraryHashes=dependencies,
        coverageScope='COMPLETE_THREE_REQUESTS_THREE_REPOSITORIES_NO_CODE_INTERFACE',whole451Accepted=False,
        historicalSuccessTransferred=False,coverageUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=52,suites=7,units=units,targetUnitsFour100=result['targetUnitsFour100'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
