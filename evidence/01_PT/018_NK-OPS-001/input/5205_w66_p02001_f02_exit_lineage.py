"""Reconcile the public P020 fixture receipt with the current tool tree and the F02 exit."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

RECORDS = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
START = RECORDS / '485_P02001比較工具とF02終了依存開始.json'
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
OLD = OPS / 'PG37324-p020-whole142-independent-v1'
GOVERNANCE = OPS / 'PG37326-p020-current-criteria-return-v1/manifest.json'
FOUR = OPS / 'PG39616-wbs66-four-module-edge-and-handoff-v1/manifest.json'
EXTERNAL = OPS / 'PG39622-f02-four-module-external-origins-delta-v1/manifest.json'
WBS = Path('/home/mini/codex/project1/work/PMO/hourly-monitor/wbs66-20261116')
PLAN = WBS / '58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す'
CHR = 'program/characterization'
BASELINE = CHR + '/baseline/current'
SS355 = ('documents/300_SS/350_運用・品質/'
         '355_Characterization Test実行準備・PG開始gate.md')
DOMAINS = ('protocol', 'storage', 'bootstrap', 'batch')


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reference(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def matching(path, commit):
    pinned = git('show', f'{commit}:{path}')
    return sha(pinned) == sha(Path(path).read_bytes())


def compare_tool(head, old):
    old_tool_source = old['source']
    directory_hash = git('rev-parse', f'{head}:{CHR}').decode().strip()
    assert git('rev-parse', f'{old_tool_source}:{CHR}').decode().strip() == directory_hash
    assert not git('diff', '--name-only', head, '--', CHR)
    pins = old['sourceTestPins']
    assert len(pins) == 283 and all(name.startswith(CHR + '/') for name in pins)
    file_entries = set(git('ls-tree', '-r', '--name-only', head, '--', CHR).decode().splitlines())
    assert set(pins) <= file_entries
    main = {name: h for name, h in pins.items() if '/src/main/java/' in name}
    assert len(main) == 6 and all(sha(Path(name).read_bytes()) == h for name, h in main.items())
    baseline = {name: h for name, h in pins.items() if name.startswith(BASELINE + '/')}
    assert len(baseline) == 27
    assert set(baseline) == {name for name in file_entries if name.startswith(BASELINE + '/')}
    assert all(sha(Path(name).read_bytes()) == h for name, h in baseline.items())
    assert git('rev-parse', f'{head}:{BASELINE}') == git('rev-parse', f'843de94:{BASELINE}')
    return dict(publishedToolTree=directory_hash, inputPathsInIdenticalGitTree=len(pins),
                directlyHashedMain=main, directlyHashedCurrentBaseline=baseline,
                baselineMatchesGateCommit='843de94', testAndReportBodiesReopened=0)


def old_tool_terminal(old, governance):
    original_terminal = reference(OLD / 'terminal.json')
    assert original_terminal['sha256'] == old['files']['terminal.json']
    terminal = read(original_terminal['path'])
    assert terminal['actualExit'] == old['actualExit'] == 0
    assert terminal['source'] == governance['source'] == old['source']
    assert terminal['sourceInputsUnchanged'] and terminal['baselineUnchanged']
    assert all(stat['actualExit'] == 0 and not stat['timedOut']
               for stat in terminal['stages'].values())
    expected = {name: dict(missed=0, covered=count) for name, count in
                {'LINE': 1464, 'METHOD': 232, 'CLASS': 12, 'BRANCH': 897, 'INSTRUCTION': 7800}.items()}
    assert old['rawCounters'] == governance['rawCounters'] == expected
    physical = old['classSha256']
    static = old['actualBytesStaticProof']
    assert reference(Path(static['path'])) == static
    static_data = read(static['path'])
    assert static_data['all16ActualBytesSpotbugsBugsMissingErrors0']
    assert static_data['mainClassHashes'] == physical
    assert len(physical) == 16 and not old['oldExecUnion'] and not old['manualCoverageExclusions']
    actual = []
    for name, expected_hash in old['files'].items():
        if not name.startswith('xml/'):
            continue
        file = OLD / name
        assert reference(file)['sha256'] == expected_hash
        root = ET.parse(file).getroot()
        assert all(int(root.get(key, '0')) == 0 for key in ('failures', 'errors', 'skipped'))
        for case in root.findall('testcase'):
            assert all(child.tag in {'system-out', 'system-err'} for child in case)
            actual.append((case.get('classname'), case.get('name')))
    assert len(actual) == len(set(actual)) == old['success'] == 142
    assert set(actual) == {(row['className'], row['name']) for row in old['cases']
                           if row['result'] == 'PASS'}
    assert all(old[name] == 0 for name in ('failed', 'errors', 'skipped', 'notRun'))
    assert reference(Path(governance['matrix']['path'])) == governance['matrix']
    return dict(originalSource=old['source'], originalRun=old['run'], terminal=original_terminal,
                passedCases=len(actual), suites=old['wholeSuites'], rawCounters=expected,
                physical=16, applicableStaticProof=static,
                individualMatrix=governance['matrix'], newExecutions=0)


def compare_f02(core):
    proof = read(FOUR)
    external = read(EXTERNAL)
    assert proof['actualExit'] == proof['historicalBuildActualExit'] == external['actualExit'] == 0
    assert proof['currentFourEligibleSourceEquality'] == dict(all490=True, main=482, poms=8)
    paths = [f'src/schubert-nk-{name}/src/main' for name in DOMAINS] + ['pom.xml']
    assert not git('diff', '--name-only', proof['source'], core, '--', *paths)
    poms = proof['sixPomDeclaration']['pomHashes']
    assert len(poms) == 8 and all(matching(name, core) and sha(Path(name).read_bytes()) == h
                                  for name, h in poms.items())
    assert set(proof['f02PhysicalEdges']['actualPhysicalCount']) == set(DOMAINS)
    assert sum(proof['f02PhysicalEdges']['actualPhysicalCount'].values()) == 1101
    assert proof['f02PhysicalEdges']['storageSqlEdgeStillOpen']
    assert external['currentReferencePairs'] == 385 and not external['wholeSixVerified']
    assert not external['unconfirmedNameReferences'] and not external['ambiguousOrigins']
    return dict(fourModuleCurrentQualifiedInputs=490, productModulesWithTypeAndBytecodeProof=list(DOMAINS),
                publishedExternalSymbolPairs=385, sixPomInputsOnly=len(poms),
                missingTypedModules=['api', 'web'], protectedWholeTypeGate='QA-056',
                storagePhysicalSqlEdge='BUG-3233_OPEN', runtimeReceipt='REQUIRED_PENDING',
                whole451='NOT_ACCEPTED', handoff=reference(FOUR), staticOrigins=reference(EXTERNAL))


def main():
    group = read(START)
    values = group['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    core = values['productionCoreMain']
    assert head == values['source'] and not git('diff', '--name-only', core, head, '--', 'src')
    old = read(OLD / 'manifest.json')
    governance = read(GOVERNANCE)
    design = git('show', f'origin/main:{SS355}')
    assert sha(design) == governance['canonicalSS355Sha256'] == sha(Path(SS355).read_bytes())
    wbs_path = PLAN / '190元項目から条件と終端判断を引く.tsv'
    wbs = [line.split('\t') for line in wbs_path.read_text().splitlines()
           if line.startswith(('WBS-F02\t', 'WBS-P020-01\t'))]
    assert len(wbs) == 2 and all(row[1] == 'NOT_ACCEPTED' for row in wbs)
    children = []
    for row in governance['children']:
        assert row['acceptance'] == row['exitDependencyStatus'] == 'NOT_ACCEPTED'
        checks = row['individualChecks']
        assert len(checks) == 2 and all(reference(Path(c['evidence']['path'])) == c['evidence']
                                        for c in checks)
        children.append(dict(wbs=row['wbsLeaf'], locallyApplicable=[c['id'] for c in checks],
                             exitDependency=row['exitDependency'], formal='NOT_ACCEPTED'))
    assert [row['exitDependency'] for row in children] == [
        'WBS-F02', 'WBS-P020-01.01', 'WBS-P020-01.02']
    evidence = dict(actualExit=0, currentHead=head, productionCoreMain=core,
                    groupStart=group['eventId'], canonicalDesignSha256=sha(design),
                    exactTool=compare_tool(head, old), historicalToolExecution=old_tool_terminal(old, governance),
                    wbs=reference(wbs_path), localCriteria=children, f02=compare_f02(core),
                    productTests=0, currentCoverageAdded=0, newAcceptance=0,
                    actualChrCompleted=False, baselineWrites=0, whole451Accepted=False,
                    verifier=reference(Path(__file__)),
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    file = OPS / values['run'] / 'manifest.json'
    with file.open('x') as out:
        json.dump(evidence, out, indent=2, ensure_ascii=False)
        out.write('\n')
    print(reference(file))


if __name__ == '__main__':
    main()
