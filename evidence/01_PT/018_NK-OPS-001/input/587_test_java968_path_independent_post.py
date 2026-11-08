"""Check Test path inventory against committed tree metadata, without Test body IO."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import json
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = B / 'evidence/PG23942-test-java968-index-metadata-v1'
O = B / 'evidence/PG23944-test-java968-index-independent-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
HELD = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java'}
MODULES = {'schubert-nk-api':306,'schubert-nk-batch':282,'schubert-nk-bootstrap':60,
           'schubert-nk-protocol':25,'schubert-nk-storage':31,'schubert-nk-web':264}


def validate(rows, tree, artifacts, mains):
    assert len(rows) == len({v['path'] for v in rows}) == 968
    assert {v['path'] for v in rows} == set(tree)
    assert dict(Counter(v['module'] for v in rows)) == MODULES
    matches = 0
    for row in rows:
        n = row['path']
        assert Path(n).name not in HELD
        mode, object_id = tree[n]
        assert row['gitIndexMode'] == mode and row['gitBlobObjectIdSHA1'] == object_id
        assert row['module'] == n.split('/')[1]
        candidate = n.replace('/src/test/java/', '/src/main/java/')
        if Path(n).name.endswith('Test.java'):
            candidate = str(Path(candidate).with_name(Path(n).name.removesuffix('Test.java') + '.java'))
        else:
            candidate = None
        expected = candidate if candidate in mains else None
        assert row['candidateMainByName'] == expected
        assert row['candidateOwnerByName'] == (artifacts[expected]['owner'] if expected else None)
        assert row['candidateCostOwnerByName'] == (artifacts[expected]['costOwner'] if expected else None)
        matches += expected is not None
        assert row['sourceBodySha256'] is None and row['confirmedOwner'] is None and row['testCaseIds'] is None
        for field in ('sourceBodyReviewed','sourceContentReadByIndexer','namingMatchConfirmsOwnership',
                      'testPassInferred','actualRuntimeEvidenceInferred'):
            assert row[field] is False
        assert row['executionEvidenceStatus'] == 'NOT_JOINED_BY_THIS_INDEX_EXISTING_RESULTS_UNCHANGED'
    return matches


def main():
    assert not O.exists()
    m = load(P / 'manifest.json')
    assert m['actualExit'] == 0 and m['productTestsExecuted'] == 0 and m['testCaseCountInferred'] is False
    cp = R / m['config']['path']
    assert sha(cp) == m['config']['sha256']
    cfg = load(cp)
    head = cfg['gitSnapshotHead']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == head
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only',head,'--','src'],cwd=R,text=True).splitlines()
    tests = [n for n in paths if '/src/test/java/' in n and n.endswith('.java')]
    assert len(tests) == 970
    excluded = [n for n in tests if Path(n).name in HELD]
    eligible = sorted(n for n in tests if Path(n).name not in HELD)
    assert len(excluded) == 2 and sorted(excluded) == sorted(cfg['heldExcludedNamesOnly']) == sorted(m['excludedHeldNamesOnly'])
    # Only eligible literals are given to the command that reads blob identities.
    data = subprocess.check_output(['git','--literal-pathspecs','ls-tree','-r','-z',head,'--',*eligible],cwd=R)
    tree = {}
    for item in data.decode().strip('\0').split('\0'):
        left, name = item.split('\t',1)
        mode, kind, object_id = left.split()
        assert name in eligible and Path(name).name not in HELD and kind == 'blob'
        assert name not in tree
        tree[name] = (mode,object_id)
    ref = R / m['indexReference']['path']
    assert sha(ref) == m['indexReference']['sha256']
    rows = load(ref)
    before_bytes = subprocess.check_output(['git','show',head+':'+cfg['inventory']['path']],cwd=R)
    assert hashlib.sha256(before_bytes).hexdigest() == cfg['inventory']['sha256']
    before = json.loads(before_bytes)
    artifacts = {v['path']:v for v in before['artifacts']}
    mains = {n for n in paths if '/src/main/java/' in n and n.endswith('.java')}
    assert len(mains) == 967 and mains <= set(artifacts)
    matches = validate(rows,tree,artifacts,mains)
    assert matches == 459 == m['namingOnlyCandidateMatches']
    wp = R / cfg['inventory']['path']
    ap = R / cfg['acceptance']['path']
    assert sha(wp) == m['inventoryAfter']['sha256'] and sha(ap) == m['acceptanceAfter']['sha256']
    current = load(wp)
    overlay = current.pop('currentTestJava968PathIndex20261108')
    assert current == before and overlay['reference'] == m['indexReference']
    assert overlay['indexedTestJavaPaths'] == 968 and overlay['namingOnlyCandidateMatches'] == 459
    assert overlay['confirmedOwnershipInferred'] is False and overlay['testCasesOrPassInferred'] is False
    old_acceptance = subprocess.check_output(['git','show',head+':'+cfg['acceptance']['path']],cwd=R)
    assert hashlib.sha256(old_acceptance).hexdigest() == cfg['acceptance']['sha256']
    actual = load(ap)
    assert actual['inventorySha256'] == sha(wp)
    original = json.loads(old_acceptance)
    actual['inventorySha256'] = original['inventorySha256']
    assert actual == original
    negatives = []
    for field, value in [('gitBlobObjectIdSHA1','0'*40),('candidateOwnerByName','WBS-G04'),
                         ('confirmedOwner','WBS-G04'),('testCaseIds',['INVENTED-PASS']),
                         ('sourceBodyReviewed',True),('sourceContentReadByIndexer',True),
                         ('namingMatchConfirmsOwnership',True),('testPassInferred',True),
                         ('actualRuntimeEvidenceInferred',True),('executionEvidenceStatus','PASS')]:
        changed = deepcopy(rows)
        changed[0][field] = value
        try:
            validate(changed,tree,artifacts,mains)
        except AssertionError:
            negatives.append(field)
        else:
            raise AssertionError('metadata mutation accepted: '+field)
    for name, changed in [('missing',rows[:-1]),('duplicate',rows[:-1]+[rows[0]])]:
        try:
            validate(changed,tree,artifacts,mains)
        except AssertionError:
            negatives.append(name)
        else:
            raise AssertionError('metadata mutation accepted: '+name)
    O.mkdir()
    result = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],
                  producerManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),
                  indexedTestJavaPaths=968,excludedHeldNameCount=2,moduleCounts=MODULES,
                  committedTreeAndIndexIdentitiesMatch=True,namingOnlyCandidateMatches=459,
                  noSameNameMainCandidate=509,confirmedOwnershipInferred=False,testCaseCountInferred=False,
                  productionArtifactsUnchanged=True,productionArtifactCount=1061,
                  otherWbsValuesUnchanged=True,acceptanceReferenceReboundSameSave=True,
                  explicitTestBodyReads=0,explicitTestBodyHashComputations=0,sourceBodyReviewed=False,
                  metadataNegatives=negatives,productTestsExecuted=0,compilerOrJvmExecuted=False,
                  actualBackendActions=0,newAcceptance=0,formalUpdated=False,effortRate=None,
                  wholeTraceAccepted=False,whole451Accepted=False,
                  tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,indexedPaths=968,namingCandidates=459,metadataNegatives=len(negatives),manifestSha256=sha(O/'manifest.json'))))


if __name__ == '__main__':
    main()
