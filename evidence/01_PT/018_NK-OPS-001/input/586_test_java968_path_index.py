"""Index explicitly allowed Test filenames/blob IDs only; never open a Test body."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import importlib.util
import json
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
C = B / 'input/584_test_java968_path_index_scope.json'
O = B / 'evidence/PG23942-test-java968-index-metadata-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    assert not O.exists()
    cfg = load(C)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == cfg['gitSnapshotHead']
    names = subprocess.check_output(['git', 'ls-files', '-z', 'src/*/src/test/java/**/*.java'], cwd=R).decode().strip('\0').split('\0')
    assert len(names) == len(set(names)) == 970
    forbidden = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java'}
    excluded = [n for n in names if Path(n).name in forbidden]
    allowed = sorted(n for n in names if Path(n).name not in forbidden)
    assert sorted(excluded) == sorted(cfg['heldExcludedNamesOnly']) and len(excluded) == 2 and len(allowed) == 968
    # Explicit literal remaining path arguments exclude both held files BEFORE identity access.
    raw = subprocess.check_output(['git', '--literal-pathspecs', 'ls-files', '--stage', '-z', '--', *allowed], cwd=R)
    index = {}
    for line in raw.decode().strip('\0').split('\0'):
        head, name = line.split('\t', 1)
        mode, object_id, stage = head.split()
        assert name in allowed and Path(name).name not in forbidden and stage == '0'
        assert name not in index
        index[name] = (mode, object_id)
    assert sorted(index) == allowed
    wp = R / cfg['inventory']['path']
    ap = R / cfg['acceptance']['path']
    assert sha(wp.read_bytes()) == cfg['inventory']['sha256'] and sha(ap.read_bytes()) == cfg['acceptance']['sha256']
    wb = load(wp)
    artifacts = {v['path']: v for v in wb['artifacts']}
    assert len(artifacts) == 1061 and not any('/src/test/' in n for n in artifacts)
    main_paths = set(subprocess.check_output(['git', 'ls-files', '-z', 'src/*/src/main/java/**/*.java'], cwd=R).decode().strip('\0').split('\0'))
    assert len(main_paths) == 967 and main_paths <= set(artifacts)
    rows = []
    for name in allowed:
        base = Path(name).name
        candidate = name.replace('/src/test/java/', '/src/main/java/')
        candidate = candidate[:-9] + '.java' if candidate.endswith('Test.java') else None
        match = artifacts[candidate] if candidate in main_paths else None
        rows.append(dict(path=name,module=name.split('/')[1],gitIndexMode=index[name][0],gitBlobObjectIdSHA1=index[name][1],
                         sourceBodySha256=None,sourceBodyReviewed=False,sourceContentReadByIndexer=False,
                         fileNameConvention='TEST_SUFFIX_NOT_JUNIT_PROOF' if base.endswith('Test.java') else 'SUPPORT_OR_OTHER_FILENAME_NOT_ROLE_PROOF',
                         candidateMainByName=candidate if match else None,
                         candidateOwnerByName=match['owner'] if match else None,
                         candidateCostOwnerByName=match['costOwner'] if match else None,
                         namingMatchConfirmsOwnership=False,confirmedOwner=None,testCaseIds=None,
                         executionEvidenceStatus='NOT_JOINED_BY_THIS_INDEX_EXISTING_RESULTS_UNCHANGED',
                         testPassInferred=False,actualRuntimeEvidenceInferred=False))
    modules = dict(Counter(v['module'] for v in rows))
    assert modules == cfg['moduleCounts']
    data = (json.dumps(rows,ensure_ascii=False,indent=2)+'\n').encode()
    key = 'currentTestJava968PathIndex20261108'
    assert key not in wb
    wb[key] = dict(snapshotHead=cfg['gitSnapshotHead'],productionMainSource=cfg['source'],indexedTestJavaPaths=968,
                   excludedHeldNamesOnly=excluded,scope=cfg['scope'],moduleCounts=modules,
                   reference=dict(path=str((O/'test-java-index.json').relative_to(R)),sha256=sha(data)),
                   namingOnlyCandidateMatches=sum(v['candidateMainByName'] is not None for v in rows),
                   sourceBodyReviewed=False,confirmedOwnershipInferred=False,testCasesOrPassInferred=False,
                   originalProductionArtifacts=1061,originalProductionMainPaths=967,
                   newProductTests=0,newAcceptance=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
    new_wb = (json.dumps(wb,ensure_ascii=False,indent=2)+'\n').encode()
    old_acceptance = ap.read_bytes()
    old_pin = load(ap)['inventorySha256']
    assert old_pin == cfg['inventory']['sha256']
    old_token = ('"inventorySha256": "'+old_pin+'"').encode()
    new_token = ('"inventorySha256": "'+sha(new_wb)+'"').encode()
    assert old_acceptance.count(old_token) == 1
    new_acceptance = old_acceptance.replace(old_token,new_token,1)
    gp = B/'input/580_wbs_inventory_reference_guard.py'
    spec = importlib.util.spec_from_file_location('wbs_reference_guard_definition_only',gp)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    assert guard.validate_bytes(new_wb,new_acceptance)['bindingValid'] is True
    O.mkdir()
    (O/'test-java-index.json').write_bytes(data)
    wp.write_bytes(new_wb)
    ap.write_bytes(new_acceptance)
    out = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],
               gitSnapshotHead=cfg['gitSnapshotHead'],config=dict(path=str(C.relative_to(R)),sha256=sha(C.read_bytes())),
               indexedTestJavaPaths=968,excludedHeldNamesOnly=excluded,moduleCounts=modules,
               namingOnlyCandidateMatches=wb[key]['namingOnlyCandidateMatches'],
               indexReference=dict(path=str((O/'test-java-index.json').relative_to(R)),sha256=sha(data)),
               inventoryBefore=cfg['inventory'],inventoryAfter=dict(path=cfg['inventory']['path'],sha256=sha(new_wb)),
               acceptanceBefore=cfg['acceptance'],acceptanceAfter=dict(path=cfg['acceptance']['path'],sha256=sha(new_acceptance)),
               overlayKey=key,productionArtifactsUnchanged=True,productionArtifactCount=1061,
               sourceBodyReadByIndexer=0,sourceBodyHashComputed=0,sourceBodyReviewed=False,
               productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,
               confirmedOwnershipInferred=False,testCaseCountInferred=False,wholeTraceAccepted=False,
               newAcceptance=0,formalUpdated=False,effortRate=None,
               tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__).read_bytes())))
    (O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,indexedPaths=968,namingCandidates=out['namingOnlyCandidateMatches'],manifestSha256=sha((O/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
