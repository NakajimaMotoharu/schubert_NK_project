"""Bind four fixed-value diagnostics to the original independent test and raw measurement."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = OPS / 'PG37452-p01810-independent-case-catalog-v1/planned93-independent-cases.json'
POST = OPS / 'PG35212-maintenance-data8-post-v1/manifest.json'
RAW = OPS / 'PG35214-maintenance-data8-unfiltered-v1/manifest.json'
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/489_P01810保守値四診断の照合開始.json')
NAMESPACE = 'dev.codex.schubert.nk.batch.repository.'
CASES = {
    '080': ('BatchRun', 'MaintenanceDataValueContractTest',
            'mvalue001RunActivationCompletionAndStateKeepAllComponentsAndClosedOutcome',
            'BatchRun[identity/cutoff=<redacted>]', 'RUN'),
    '088': ('MaintenanceActivation', 'MaintenanceDataValueContractTest',
            'mvalue001RunActivationCompletionAndStateKeepAllComponentsAndClosedOutcome',
            'MaintenanceActivation[identity/cutoff=<redacted>]', 'ACTIVE'),
    '089': ('MaintenanceCompletion', 'MaintenanceRunStateValuesTest',
            'closedOutcomesHaveFixedCodesAndRedactedCompletion',
            'MaintenanceCompletion[identity/time=<redacted>]', 'completion'),
    '091': ('MaintenanceRunState', 'MaintenanceDataValueContractTest',
            'mvalue001RunActivationCompletionAndStateKeepAllComponentsAndClosedOutcome',
            'MaintenanceRunState[redacted]', 'doneData'),
}


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def method_body(text, name):
    anchor = f'void {name}('
    assert text.count(anchor) == 1
    start = text.index(anchor)
    end = text.find('\n  }', start)
    assert end > start
    return text[start:end]


def main():
    start = read(START)
    original, raw = read(POST), read(RAW)
    current = start['values']['source']
    core = start['values']['productionCoreMain']
    assert current == git('rev-parse', 'HEAD').decode().strip()
    assert not git('diff', '--name-only', core, current, '--', 'src')
    assert original['actualExit'] == raw['actualExit'] == 0
    assert original['source'] == raw['actualUnitSource']
    assert original['tests'] == 8 and raw['own5BatchSource6PhysicalRawFour100']
    assert original['oldExecCombined'] is raw['oldExecCombined'] is False
    assert original['manualCoverageExclusions'] == [] and raw['manualExclusions'] == 0
    # Audit the input graph before using any local measurement, including both full source tests.
    input_hashes = original['inputHashes']
    for path, expected in input_hashes.items():
        assert sha(git('show', f"{original['source']}:{path}")) == expected, ('original', path)
        assert sha(git('show', f'{current}:{path}')) == expected, ('current', path)
        assert sha(Path(path).read_bytes()) == expected, ('working', path)
    xml = POST.with_name('original-TEST-junit-jupiter.xml')
    assert ref(xml)['sha256'] == original['files'][xml.name]
    suite = ET.parse(xml).getroot()
    assert all(int(suite.get(key, 0)) == 0 for key in ('errors', 'failures', 'skipped'))
    found = {(c.get('classname'), c.get('name')): c for c in suite.findall('testcase')}
    assert len(found) == 8
    assert not any(c.tag in {'error', 'failure', 'skipped'} for case in found.values() for c in case)
    joined = raw['originalPost']
    assert ref(Path(joined['path'])) == joined
    raw_exec = raw['originalSingleExec']
    assert ref(Path(raw_exec['path'])) == raw_exec and raw_exec['sha256'] == original['files']['jacoco.exec']
    plans = {a['plannedCaseId']: a for a in read(PLAN)}
    assert len(plans) == 93
    out = []
    for number, (owner, test, method, expected, receiver) in CASES.items():
        case_id = 'PT-P01810-CATALOG-' + number
        row = plans[case_id]
        source = Path(row['source'])
        assert source.name == owner + '.java' and str(source) in input_hashes
        [testpath] = [Path(name) for name in input_hashes if name.endswith(f'/{test}.java')]
        assert str(testpath) in row['actualCandidateTestSourceRefs']
        body = method_body(testpath.read_text(), method)
        assert f'assertEquals("{expected}", {receiver}.toString())' in body
        assert (NAMESPACE + test, method + '()') in found
        cname = NAMESPACE.replace('.', '/') + owner
        [value] = [v for v in raw['methods'] if v['className'] == cname and v['name'] == 'toString']
        assert value['descriptor'] == '()Ljava/lang/String;'
        assert value['counters']['LINE'] == value['counters']['METHOD'] == dict(missed=0, covered=1)
        assert value['counters']['INSTRUCTION'] == dict(missed=0, covered=2)
        assert value['counters']['BRANCH'] == dict(missed=0, covered=0)
        out.append(dict(case=case_id, originalOwners=row['owners'], target=ref(source),
                        actualTest=ref(testpath), actualMethod=f'{test}#{method}',
                        literalExpected=expected, coveredOriginalRaw=value['counters'],
                        measuredOriginalClassSha256=raw['classFileHashes'][cname + '.class'],
                        measuredOriginalCrc=original['classIds'][cname],
                        classification='EXACT_ORDINARY_DIAGNOSTIC_PROOF'))
    final = dict(actualExit=0, groupStart=start['eventId'], checkedHead=current, productionCoreMain=core,
                 sourceFixedOriginal=original['source'], runOriginal=original['run'],
                 originalWholeTests=8, originalHashExactInputs=len(input_hashes),
                 originalRaw=ref(RAW), originalPost=ref(POST), originalPublicXml=ref(xml),
                 originalCatalog=ref(PLAN), sameSourceLocalCriteria=out,
                 finalOperationalSinkProof=False, whole451Accepted=False, formalUpdated=False,
                 testsExecuted=0, measuredProductCoverageAdded=0, newAcceptance=0,
                 terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(Path(__file__)))
    target = OPS / start['values']['run'] / 'manifest.json'
    with target.open('x') as stream:
        json.dump(final, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(ref(target))


if __name__ == '__main__':
    main()
