"""Independent exact eleven XML/source/session/CRC and whole-class counters, no product rerun."""
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
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
SLOT = WORK / 'pg9682-semantic-component-post-v1'
OUT = BASE / 'PG9682-semantic-component-post-v1'
RUN = WORK / 'pg9680-semantic-component-host-v1'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
NORMAL = WORK / 'pg9660-pagination-six-compile-v1/snapshot'
TARGET = 'dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator'
PREFIX = 'dev.codex.schubert.nk.protocol.layout.'
EXPECTED = {
    PREFIX + 'PayloadPaginationBoundaryTest': {
        'page001SecondPageHasIndependentExpectedBounds',
        'page002MaximumEffectivePageKeepsExactNineDigitArithmetic',
        'page003RejectsIndependentRangeAndOneFieldArithmeticChanges'},
    PREFIX + 'PayloadSemanticValidatorTest': {
        'pageConstantsCountsAndArithmeticAreEnforced','listRecordConditionsAndOrderingAreEnforced',
        'scenarioInlineAndLargeFileConditionsAreEnforced','mediaAnimationAndMusicConditionsAreEnforced',
        'loginUserPasswordDateAndSessionRulesAreEnforced','notificationCancellationAndQuestionStateConditionsAreEnforced',
        'receiptWebAndDefensiveContractsAreEnforced','deletedNotificationNeverContainsAnswer'}}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    raw = data.read_checked(RUN / 'manifest.safe.json','7a06c3b436db2b6038557654d66034f10a2659015793d088b4007f6a9ea28637')
    normal = data.read_checked(data.BASE / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    assert raw['actualExit'] == normal['actualExit'] == 0 and raw['source'] == normal['source'] == SOURCE
    assert raw['begin']['selectedSuites'] == {k.rpartition('.')[2]:len(v) for k,v in EXPECTED.items()}
    assert len(raw['stages']) == 2 and all(s['actualExit'] == 0 and not s['timedOut'] for s in raw['stages'])
    expected = {(cls,name) for cls,names in EXPECTED.items() for name in names}
    assert len(expected) == len(raw['cases']) == 11
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
    assert summary.read_text() == 'found=11;started=11;succeeded=11;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    for group in ('dependencyHashes','testSourceHashes'):
        assert all(data.sha(Path(p).read_bytes()) == h for p,h in raw['begin'][group].items())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert data.sha((RUN / 'jacoco.exec').read_bytes()) == raw['execSha256']
    os.umask(0o077)
    SLOT.mkdir()
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    with zipfile.ZipFile(jar) as archive:
        assert {p for p in archive.namelist() if p == TARGET + '.class' or p.startswith(TARGET + '$')} == {TARGET + '.class'}
        target = SLOT / 'PayloadSemanticValidator.class'
        with target.open('xb') as stream:
            stream.write(archive.read(TARGET + '.class'))
    helper = ROOT / 'tools/quality/architecture/SemanticComponentCoverageMeasure.java'
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
    stages.append(steps.step('measure-whole-class',[str(tc / 'jdk-25.0.4/bin/java'),'-cp',str(reader) + os.pathsep + cp,helper.stem,str(RUN / 'jacoco.exec'),str(target)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    lines = (SLOT / 'measure-whole-class.stdout').read_text().splitlines()
    first = lines[0].split('\t')
    assert first[:2] == ['CLASS',TARGET]
    counters = {}
    method_rows = []
    line_rows = []
    for line in lines[1:]:
        values = line.split('\t')
        if values[0] == 'COUNTER':
            _,kind,missed,covered = values
            assert kind not in counters
            counters[kind] = dict(missed=int(missed),covered=int(covered))
        elif values[0] == 'METHOD':
            _,name,desc,missed_line,covered_line,missed_branch,covered_branch = values
            method_rows.append(dict(name=name,descriptor=desc,missedLine=int(missed_line),coveredLine=int(covered_line),missedBranch=int(missed_branch),coveredBranch=int(covered_branch)))
        else:
            assert values[0] == 'LINE'
            _,number,missed,covered,missed_branch,covered_branch = values
            line_rows.append(dict(line=int(number),missedInstruction=int(missed),coveredInstruction=int(covered),missedBranch=int(missed_branch),coveredBranch=int(covered_branch)))
    assert set(counters) == {'LINE','METHOD','CLASS','BRANCH'}
    assert len(method_rows) == 38 and len(line_rows) == 315
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    verify(invocation)
    OUT.mkdir()
    for name in xmls:
        with (OUT / name).open('xb') as stream:
            stream.write((RUN / 'xml' / name).read_bytes())
    with (OUT / 'summary.safe.txt').open('xb') as stream:
        stream.write(summary.read_bytes())
    data.write(OUT / 'whole-validator-detail.json',dict(methods=method_rows,lines=line_rows))
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,actualTests=11,suites=2,newTestIds=0,
        hostManifestSha256='7a06c3b436db2b6038557654d66034f10a2659015793d088b4007f6a9ea28637',
        cases={k:sorted(v) for k,v in EXPECTED.items()},xmlHashes=xmls,summarySha256=data.sha(summary.read_bytes()),
        execSha256=raw['execSha256'],wholeSourceUnitCounters=counters,wholeClassFour100=all(c['missed'] == 0 for c in counters.values()),
        crc64=first[2],sessionId='PG9680-PROTOCOL-SEMANTIC-COMPONENT',physicalClassSha256=data.sha(target.read_bytes()),
        reportHelperSha256=helper_sha,reportLibraryHashes=deps,reportStages=stages,
        detailSha256=data.sha((OUT / 'whole-validator-detail.json').read_bytes()),
        failed=0,errors=0,skipped=0,aborted=0,productTestsExecutedByPost=0,coverageUnion=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,programPtComplete=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=11,wholeSourceUnitCounters=counters,wholeClassFour100=result['wholeClassFour100'],manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
