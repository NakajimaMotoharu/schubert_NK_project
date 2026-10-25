"""Independent eight-method XML and single-session User query unit/method counter measurement."""
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
SOURCE = '70165b0768a1fabd13371cc25a55978fcf3452ba'
WORK = ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg9972-plain-core-fixed-host-v1'
SLOT = WORK/'pg9974-plain-core-fixed-post-v1'
OUT = BASE/'PG9974-plain-core-fixed-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE/'PG9970-plain-core-fixed-preflight-v1/manifest.json',
        '1e7d41bc27f086663ab78e20018172751eb186fb71f4b9f421eeed583756b7b3')
    host_sha = 'b1418cab0a64990e600c40daeee584864bf6eda522187ac5adab9c846ac8f76e'
    host = data.read_checked(BASE/'PG9972-plain-core-fixed-host-v1/manifest.json',host_sha)
    assert prepared['actualExit'] == host['actualExit'] == 0 and prepared['source'] == host['source'] == SOURCE
    assert (prepared['expectedTests'],prepared['expectedSuites']) == (host['begin']['expectedTests'],host['begin']['expectedSuites']) == (8,2)
    cases = data.read_checked(BASE/'PG9970-plain-core-fixed-preflight-v1/cases.json',prepared['casesSha256'])
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
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=8;started=8;succeeded=8;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**host['begin']['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    normal = data.read_checked(BASE/'PG9968-plain-core-fixed-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-codec'
    classes.mkdir()
    with zipfile.ZipFile(jar) as archive:
        for name,digest in prepared['physicalMainClasses'].items():
            assert name.startswith('dev/codex/schubert/nk/api/application/admin/') and '..' not in Path(name).parts
            raw = archive.read(name)
            assert data.sha(raw) == digest
            target = classes/name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                stream.write(raw)
    assert len(prepared['physicalMainClasses']) == 1
    helper = ROOT/'tools/quality/architecture/UserQueryPlainCoreCoverageMeasure.java'
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
    session = parse_session(lines[0].split(chr(9)),'PG9972-PLAIN-QUERY-CORE')
    header = lines[1].split(chr(9))
    assert header[:2] == ['CLASS','dev/codex/schubert/nk/api/application/admin/UserQueryRequest'] and len(header) == 3
    counters,method_counters = {},{}
    for line in lines[2:]:
        parts = line.split(chr(9))
        if parts[0] == 'METHOD':
            assert parts == ['METHOD','validateResponse','(Ldev/codex/schubert/nk/protocol/layout/TypedPayloadValues;)V']
            continue
        kind,label,miss,hit = parts
        target = counters if kind == 'COUNTER' else method_counters
        assert kind in ('COUNTER','METHOD_COUNTER') and label not in target
        target[label] = dict(missed=int(miss),covered=int(hit))
    applicable = classify(counters)
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    for path in (RUN/'xml').glob('TEST-*.xml'):
        (OUT/path.name).write_bytes(path.read_bytes())
    (OUT/'coverage.txt').write_text(text)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,hostManifestSha256=host_sha,stages=stages,
        tests=8,suites=2,newTestIds=4,xmlHashes=xmls,summaryTests=8,expectedTests=8,expectedSuites=2,
        session=session,sessionSchemaVectors=schema_vectors,execSha256=host['execSha256'],classCrc64=header[2],
        physicalMainClasses=prepared['physicalMainClasses'],counters=counters,methodCounters=method_counters,counterApplicability=applicable,
        targetUnitFour100=applicable=='FOUR100_MEASURED_APPLICABLE',helperSha256=helper_sha,libraryHashes=dependencies,
        coverageScope='COMPLETE_USER_QUERY_REQUEST_SOURCE_UNIT_PARTIAL_EXPECTED',whole451Accepted=False,
        historicalSuccessTransferred=False,coverageUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=8,suites=2,counters=counters,targetUnitFour100=result['targetUnitFour100'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
