"""Prove single current resource-scope run and four-module consumer byte compatibility."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

OPS = Path('evidence/01_PT/018_NK-OPS-001')
E = OPS / 'evidence'
PROFILE = OPS / 'input/5210_process_resource_scope_local_profile.json'
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/491_F03純資源scope変更前照合開始.json')
RAW = E / 'PG39762-f03-process-resource-scope-raw-v1'
PRIOR = E / 'PG39462-admission-single-cleanup-four-build-v2/compile/manifest.json'
FOUR = E / 'PG39764-process-resource-scope-four-main-v1/compile/manifest.json'
ROOT = Path.cwd()
NAME = 'dev/codex/schubert/nk/batch/platform/ProcessResourceScope'
TARGET = NAME + '.class'
TEST_NAME = NAME.replace('/', '.') + 'ValueContractTest'
CASES = {'scopeValue001RejectsAnyInstanceOfTheStaticNamespace()',
         'scopeValue002RejectsMissingInputsWithoutAcquiringOrReleasingThem()',
         'scopeValue003OwnsEachAcquisitionThroughItsOwnRelease()',
         'scopeValue004BodyAndReleaseFollowTheIndependentLiteralPriorityTable()'}


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def check_source(base, core, fixed, config):
    target = Path(next(p for p in config['mainSources'] if p.endswith('/ProcessResourceScope.java')))
    old = git('show', f'{base}:{target}')
    current = git('show', f'{fixed}:{target}')
    assert current == target.read_bytes() == git('show', f'{core}:{target}')
    guard = b'  private ProcessResourceScope() {\n    throw new AssertionError("process resource scope is static");\n  }'
    assert current.count(guard) == 1
    assert current.replace(guard, b'  private ProcessResourceScope() {}') == old
    change_paths = git('diff', '--name-only', base, core, '--', ':(glob)src/*/src/main/java/**/*.java')
    assert change_paths.decode().splitlines() == [str(target)]
    before = Path(str(target).replace('/main/', '/test/')).with_name('ProcessResourceScopeTest.java')
    assert git('show', f'{base}:{before}') == git('show', f'{fixed}:{before}') == before.read_bytes()
    return dict(main=ref(target), prototypeExactExceptPrivateGuard=True,
                originalWholeSevenSource=ref(before), originalWholeSevenReexecuted=0)


def check_build(core, prepare):
    b = read(FOUR)
    old = read(PRIOR)
    assert b['inputHashesReverified'] and b['actualExit'] == b['productTestsExecuted'] == 0
    assert b['sourceCore'] == core and b['baselineSource'] == old['sourceCore']
    assert b['mainCounts'] == {'protocol': 169, 'storage': 25, 'bootstrap': 88, 'batch': 200}
    assert {module: len(phys) for module, phys in b['physicalClassHashes'].items()} == {
        'protocol': 176, 'storage': 79, 'bootstrap': 200, 'batch': 646}
    assert sum(map(len, b['physicalClassHashes'].values())) == 1101
    assert b['physicalClassHashes']['batch'][TARGET] == prepare['physicalClassHashes'][TARGET]
    expected_delta = {k: dict(added=[], removed=[], changed=[TARGET] if k=='batch' else [])
                      for k in b['physicalClassHashes']}
    assert b['deltas'] == expected_delta
    for filename, digest in b['logs'].items():
        assert ref(FOUR.with_name(filename))['sha256'] == digest
    assert set(b['sourceInputs']) == set(old['sourceInputs'])
    assert sum(b['sourceInputs'][name]!=digest for name, digest in old['sourceInputs'].items()) == 1
    tool = ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'
    first = Path(old['cwd']) / 'src/schubert-nk-batch/target/classes' / TARGET
    second = Path(b['cwd']) / 'src/schubert-nk-batch/target/classes' / TARGET
    assert ref(first)['sha256'] == old['physicalClassHashes']['batch'][TARGET]
    assert ref(second)['sha256'] == b['physicalClassHashes']['batch'][TARGET]
    hints = ['InspectorUnitProbe', 'SystemctlStateSource', 'ConfigurationGroupResolver']
    bdir = Path(b['cwd']) / 'src/schubert-nk-batch/target/classes'
    for hint in hints:
        entries = b['physicalClassHashes']['batch']
        klass = str(Path(TARGET).with_name(hint + '.class'))
        assert entries[klass] == old['physicalClassHashes']['batch'][klass]
        assert ref(bdir / klass)['sha256'] == entries[klass]
    def abi(path):
        return subprocess.check_output([str(tool), '-p', '-s', str(path)], timeout=10)
    assert abi(first) == abi(second)
    return dict(compile=ref(FOUR), classAbiCompared=sha(abi(second)), physicalCount=1101,
                admittedFourInputCount=490, unchangedPhysical=1100, changedTargetPhysical=1,
                sameLocalTestTargetBytes=True, unchangedConsumers=hints, wholeSix=False)


def check_raw(post, prepare):
    padded = RAW / 'raw.tsv'
    rows = [line.split('\t') for line in padded.read_text().splitlines()]
    observed = [row for row in rows if row[0]=='CLASS']
    assert {row[1]+'.class' for row in observed} == set(prepare['physicalClassHashes'])
    assert len(observed)==len(prepare['physicalClassHashes'])==13
    def counters(r):
        return {field: dict(missed=int(miss), covered=int(hit))
                for field, miss, hit in (cell.split(':') for cell in r[6:])}
    values = {r[1]: counters(r) for r in observed}
    expected = {'LINE':34,'METHOD':3,'CLASS':1,'BRANCH':22,'INSTRUCTION':107,'COMPLEXITY':14}
    assert values[NAME] == {k:dict(missed=0,covered=v) for k,v in expected.items()}
    by_method = {row[2] for row in rows if row[0]=='METHOD' and row[1]==NAME}
    assert by_method == {'<init>', 'acquire', 'use'}
    assert not [row for row in rows if row[0]=='DEFICIT' and row[1]==NAME]
    [target] = [r for r in observed if r[1]==NAME]
    assert target[2] == post['classIds'][NAME] and target[3]=='true'
    return dict(raw=ref(padded),command=ref(RAW/'raw-command.json'),rawTarget=values[NAME],
                rawSupportRemaining={k:v for k,v in values.items() if k!=NAME and
                                     any(p['missed'] for p in v.values())})


def main():
    start = read(START)
    c = read(PROFILE)
    paths = {key: Path(value) / 'manifest.json' for key, value in c['slots'].items()}
    unit, post, prepare, stat, preflight = map(read, [paths[k] for k in
        ('unit','post','prepare','static','preflight')])
    run = unit['begin']
    core, fixed = c['productionCoreMain'], post['source']
    assert run['source']==fixed and run['productionCoreMain']==post['productionCoreMain']==core
    assert prepared_gates(stat,preflight)
    assert unit['actualExit']==post['actualExit']==0 and unit['tests']==post['tests']==len(CASES)==4
    assert unit['errors']==unit['failures']==unit['skipped']==0
    assert post['actualBackendNativeFsRootOrHeldClassActions']==0
    assert post['forbiddenInitializedClassesObserved']==[] and post['oldExecCombined'] is False
    assert post['manualCoverageExclusions']==[] and post['wholeScopeFour100'] is False
    doc = paths['post'].with_name('original-TEST-junit-jupiter.xml')
    assert ref(doc)['sha256']==post['files'][doc.name]
    tdoc=ET.parse(doc).getroot()
    assert all(x.get('classname')==TEST_NAME for x in tdoc.findall('testcase'))
    assert {x.get('name') for x in tdoc.findall('testcase')}==CASES
    assert not any(child.tag in {'failure','error','skipped'}
                   for case in tdoc.findall('testcase') for child in case)
    results = dict(actualExit=0,groupStart=start['eventId'],productionCoreMain=core,source=fixed,
                   runId=run['session'],tests=4,failed=0,errors=0,skipped=0,notRun=0,
                   firstExecutedTestsPassed=4,newTestDefinitions=4,
                   sourceCompatibility=check_source(start['values']['productionCoreMain'],core,fixed,c),
                   build=check_build(core,prepare),qualification=check_raw(post,prepare),
                   publicXml=ref(doc),proofs={k:ref(v) for k,v in paths.items()},
                   rawPmd=52,staticApplicable=0,manualExclusions=0,oldExecCombined=False,
                   wholeF02Accepted=False,wholeF03Accepted=False,whole451Accepted=False,
                   actualRuntimeUnitOrOwnerProof=False,newAcceptance=0,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(),verifier=ref(Path(__file__)))
    with (RAW / 'manifest.json').open('x') as out:
        json.dump(results,out,indent=2,ensure_ascii=False)
        out.write('\n')
    print(ref(RAW / 'manifest.json'))


def prepared_gates(static, preflight):
    return (len(static['rawFindings'])==52 and len(preflight['classified'])==52 and
            all(preflight[k]==0 for k in ('staticApplicable','unclassified','checkstyle','spotbugs','processingErrors')))


if __name__=='__main__':
    main()
