"""Independent current XML, canonical fixture and complete named source-unit coverage post."""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import class_reference_metadata as classfile
import pg9346_direct_companion_jdk_post as steps
import pg9698_semantic_fixed_post as prior_cases
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
RUN = WORK / 'pg9708-named-canonical-component-host-v1'
NORMAL = WORK / 'pg9694-semantic-direct-fixed-six-compile-v1/snapshot'
SLOT = WORK / 'pg9710-named-canonical-component-post-v2'
OUT = BASE / 'PG9710-named-canonical-component-post-v2'
PREFIX = 'dev.codex.schubert.nk.protocol.layout.'
EXPECTED = {**prior_cases.EXPECTED,PREFIX + 'PayloadTypeCatalogTest': {
    'allNamedTypesHaveIndependentDirectionalFieldMeaning','explicitCatalogMatchesIndependentSs323NamedTypeFixture',
    'allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes','optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames',
    'catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes','typedModelsAndHelpersRejectNullMissingAndWrongKinds'}}
FIXTURES = {
    'named-accessors-independent.tsv':'27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5',
    'fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b',
    'named-types-ss323.tsv':'9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76'}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    raw = data.read_checked(RUN / 'manifest.safe.json','31b9e6cdb6cb0c4bdad0307550dc07e0aadacf6aadfc156f2a7f3a48a8872b4b')
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert raw['actualExit'] == normal['actualExit'] == 0 and raw['source'] == normal['source'] == SOURCE
    assert raw['begin']['selectedSuites'] == {k.rpartition('.')[2]:len(v) for k,v in EXPECTED.items()}
    assert len(raw['stages']) == 2 and all(s['actualExit'] == 0 and not s['timedOut'] for s in raw['stages'])
    expected = {(cls,name) for cls,names in EXPECTED.items() for name in names}
    assert len(expected) == len(raw['cases']) == 20
    assert Counter((c['classname'],c['name']) for c in raw['cases']) == Counter(expected)
    assert all(c['result'] == 'PASS' and not c['nonPass'] for c in raw['cases'])
    xmls = {}
    for cls,names in EXPECTED.items():
        path = RUN / 'xml' / ('TEST-' + cls + '.xml')
        report = ET.parse(path).getroot()
        assert report.get('name') == cls and {k:int(report.get(k)) for k in ('tests','failures','errors','skipped')} == dict(tests=len(names),failures=0,errors=0,skipped=0)
        cases = report.findall('testcase')
        assert len(cases) == len(names) and {c.get('name') for c in cases} == names
        assert all(c.get('classname') == cls and not list(c) for c in cases)
        xmls[path.name] = data.sha(path.read_bytes())
    assert xmls == raw['xmlHashes']
    summary = RUN / 'xml/summary.safe.txt'
    assert summary.read_text() == 'found=20;started=20;succeeded=20;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    for key in ('dependencyHashes','testSourceHashes','fixtureHashes'):
        assert all(data.sha(Path(p).read_bytes()) == h for p,h in raw['begin'][key].items())
    assert len(raw['begin']['fixtureHashes']) == 6 and Counter(raw['begin']['fixtureHashes'].values()) == Counter({h:2 for h in FIXTURES.values()})
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert data.sha((RUN / 'jacoco.exec').read_bytes()) == raw['execSha256']
    fixtures = {}
    for name,digest in FIXTURES.items():
        path = ROOT / 'src/schubert-nk-protocol/src/test/resources/protocol' / name
        assert data.sha(path.read_bytes()) == digest and subprocess.check_output(['git','show',SOURCE + ':' + str(path.relative_to(ROOT))],cwd=ROOT) == path.read_bytes()
        fixtures[name] = path.read_text()
    rows = [line.split('\t') for line in fixtures['named-types-ss323.tsv'].splitlines() if line and not line.startswith('#')]
    assert len(rows) == 64 and all(len(r) == 3 for r in rows)
    names = {name for row in rows for name in row[1:] if name != '-'}
    assert len(names) == 69 and sum(row[2] != '-' for row in rows) == 14
    subjects = names | {'PayloadTypeCatalog','TypedFieldValues','TypedPayloadValues','PayloadSemanticValidator'}
    assert len(subjects) == 73
    master = ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    inventory = json.loads(master.read_bytes())
    original_rows = inventory['artifacts']
    assert len(original_rows) == 941
    subject_rows = [r for r in original_rows if r.get('class','').rpartition('/')[2] in subjects]
    assert len(subject_rows) == 73 and {r['class'].rpartition('/')[2] for r in subject_rows} == subjects
    assert len({r['class'] for r in subject_rows}) == 73
    assert all(r['owner'] == r['costOwner'] == 'WBS-P001-03' for r in subject_rows if r['class'].rpartition('/')[2] in names)
    assert all(data.sha((ROOT / r['path']).read_bytes()) == normal['begin']['inputHashes'][r['path']] for r in subject_rows)
    internals = {r['class'] for r in subject_rows}
    source_membership = {(r['class'].rpartition('/')[0],Path(r['path']).name) for r in subject_rows}
    def valid_subject_mapping(value):
        return value == subject_rows and len({r['class'].rpartition('/')[2] for r in value}) == 73
    assert valid_subject_mapping(subject_rows)
    assert not valid_subject_mapping(subject_rows[:-1]) and not valid_subject_mapping(subject_rows + [subject_rows[0]])
    forged = [dict(r) for r in subject_rows]
    forged[0]['class'] = 'dev/codex/schubert/nk/protocol/layout/' + forged[0]['class'].rpartition('/')[2]
    if forged[0] == subject_rows[0]:
        forged[0]['class'] = 'dev/codex/schubert/nk/protocol/layout/foreign/' + forged[0]['class'].rpartition('/')[2]
    assert not valid_subject_mapping(forged)
    collision = subject_rows + [dict(subject_rows[0], **{'class':'foreign/' + subject_rows[0]['class'].rpartition('/')[2]})]
    assert not valid_subject_mapping(collision)
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT / 'complete-source-units'
    classes.mkdir()
    selected = {}
    with zipfile.ZipFile(jar) as archive:
        source_file_members = {name[:-6] for name in archive.namelist() if name.endswith('.class') and (name[:-6].rpartition('/')[0],classfile.read(archive.read(name))['sourceFile']) in source_membership}
        for name in archive.namelist():
            if name.endswith('.class') and any(name[:-6] == n or name[:-6].startswith(n + '$') for n in internals):
                assert '..' not in Path(name).parts and not Path(name).is_absolute()
                content = archive.read(name)
                target = classes / name
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(content)
                selected[name[:-6]] = data.sha(content)
    assert internals <= set(selected) and set(selected) == source_file_members
    assert set(selected) - {next(iter(selected))} != source_file_members
    assert set(selected) | {'foreign/Extra'} != source_file_members
    catalog = SLOT / 'physical-inventory.txt'
    with catalog.open('x') as stream:
        stream.write('\n'.join(sorted(selected)) + '\n')
    helper = ROOT / 'tools/quality/architecture/NamedCanonicalCoverageMeasureV2.java'
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
    stages.append(steps.step('measure-complete-units',[str(tc / 'jdk-25.0.4/bin/java'),'-cp',str(reader) + os.pathsep + cp,helper.stem,str(RUN / 'jacoco.exec'),str(classes),str(catalog)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    output = (SLOT / 'measure-complete-units.stdout').read_text().splitlines()
    session = output[0].split('\t')
    assert session[0:2] == ['SESSION','PG9708-PROTOCOL-NAMED-CANONICAL'] and int(session[2]) <= int(session[3])
    counters = {}
    misses = []
    for line in output[1:]:
        values = line.split('\t')
        if values[0] == 'CLASS':
            _,name,crc,actual = values
            assert name in selected and name not in counters
            counters[name] = dict(crc64=crc,executionDataPresent=actual == 'true',counters={})
        elif values[0] == 'COUNTER':
            _,name,kind,missed,covered = values
            assert kind not in counters[name]['counters']
            counters[name]['counters'][kind] = dict(missed=int(missed),covered=int(covered))
        else:
            assert values[0] == 'MISS_METHOD'
            _,name,method,descriptor,ml,cl,mb,cb = values
            misses.append(dict(className=name,method=method,descriptor=descriptor,missedLine=int(ml),coveredLine=int(cl),missedBranch=int(mb),coveredBranch=int(cb)))
    assert set(counters) == set(selected) and all(set(v['counters']) == {'LINE','METHOD','CLASS','BRANCH'} for v in counters.values())
    complete = sorted(n for n,v in counters.items() if all(c['missed'] == 0 for c in v['counters'].values()))
    aggregate = {kind:{field:sum(v['counters'][kind][field] for v in counters.values()) for field in ('missed','covered')} for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    assert all(data.sha((classes / (n + '.class')).read_bytes()) == h for n,h in selected.items())
    verify(invocation)
    OUT.mkdir()
    for name in xmls:
        with (OUT / name).open('xb') as stream:
            stream.write((RUN / 'xml' / name).read_bytes())
    with (OUT / 'summary.safe.txt').open('xb') as stream:
        stream.write(summary.read_bytes())
    data.write(OUT / 'source-unit-counters.json',dict(physicalClasses=counters,missedMethods=misses))
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,actualTests=20,suites=4,newTestIds=0,
        hostManifestSha256='31b9e6cdb6cb0c4bdad0307550dc07e0aadacf6aadfc156f2a7f3a48a8872b4b',
        cases={k:sorted(v) for k,v in EXPECTED.items()},xmlHashes=xmls,summarySha256=data.sha(summary.read_bytes()),
        execSha256=raw['execSha256'],sessionId=session[1],sessionStartMillis=int(session[2]),sessionEndMillis=int(session[3]),
        wholeSourceUnitCounters=aggregate,independentNamedTypes=69,sourceUnits=73,physicalClasses=len(selected),
        four100PhysicalClasses=complete,wholeSelectedFour100=len(complete) == len(selected),physicalClassHashes=selected,
        sourceUnitCountersSha256=data.sha((OUT / 'source-unit-counters.json').read_bytes()),fixtureHashes=FIXTURES,
        reportHelperSha256=helper_sha,reportLibraryHashes=deps,reportStages=stages,
        originalMasterSubjectRows=subject_rows,fullBinaryNamesFromOriginalMaster=True,sourceFileMembershipVerified=True,
        metadataCounterexamples=['missing-subject','duplicate-subject','forged-package','same-simple-name-collision','missing-physical','extra-physical'],
        failed=0,errors=0,skipped=0,aborted=0,productTestsExecutedByPost=0,coverageUnion=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,programPtComplete=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=20,physicalClasses=len(selected),four100Classes=len(complete),wholeSourceUnitCounters=aggregate,
        wholeSelectedFour100=result['wholeSelectedFour100'],manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
