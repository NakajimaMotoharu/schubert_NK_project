"""Four exact-source Main context references, never diagnostic removal or runtime reassignment."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_lgs_remaining_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
PRIOR = ('PG13608-lgs-remaining-trace-v1', '9d15f436acf7d1efd42e0c76075bcfc4d60790a7cb8099497626395eea2d78b5')
REVIEW = ('PG13633-repository-resource-context-recovery-v2', 'ad792dd4e5b1b81d24476c98144099b86c974ba46dcd3ba81d1d7a5ca2428aab')
PROOF = ('PG13637-repository-resource-context-post-recovery-v3', '52a78f4d9b7315d6eb2e7d5ec90eca2347a21893e9022e9c5b4b5c0acaf94be1')
OUT = data.BASE/'PG13640-repository-resource-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2487_API二Repository_四資源診断文脈結果.md'
NEW_IDS = {'PMD-00386', 'PMD-00387', 'PMD-00388', 'PMD-00389'}

def state_after():
    ids, refs, pending = previous_state()
    assert NEW_IDS <= ids-refs and len(ids) == 6247 and len(refs) == 3349 and len(pending) == 2488
    return ids, refs | NEW_IDS, pending | NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json', PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json', REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json', PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json', review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == 0 and proof['sourceContexts'] == proof['newSourceReasons'] == 4
    assert proof['reviewManifestSha256'] == REVIEW[1] and proof['productTestsExecuted'] == 0
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] and r['currentWholeJoinPending'] for r in rows)
    normal = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json', '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p, h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '396e7008418cb265cf8b10d5089719357957bcab'
    raw, snap = [subprocess.check_output(['git', 'show', base+':'+p], cwd=data.ROOT) for p in [INV, SNAP]]
    assert data.sha(raw) == 'db949d3670464d852874747d4be0788342203304173b4bf3c82294d0bb25cfb1'
    assert data.sha(snap) == '9befb796d1206df65c119d875ceb30b3b0a23a5b620df742520cbad89816699d'
    return prior, rows, raw, snap

def expected(prior, rows):
    ids, refs, pending = state_after()
    value = copy.deepcopy(prior)
    for name in ['invocation', 'wholeWbsAuditBefore']:
        value.pop(name, None)
    value.update(source=SOURCE, record=RECORD, sourceDerivedRaw=len(ids), mainRaw=1491, testRaw=4756,
        totalPriorCorrections=3194, joinedContextWarnings=len(refs), sourceReboundCurrentWholePending=len(pending),
        noCurrentReferenceInThisJoin=len(ids-refs),
        currentMainRepositoryStaticContexts=dict(reviewManifestSha256=REVIEW[1], proofManifestSha256=PROOF[1],
            source=SOURCE, rows=rows, newSourceReasons=4, rawRetained=4, sourceChanged=False,
            productTestsExecuted=0, currentRuntimeQualification=False, allFourAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)), sha256=PRIOR[1],
            source=SOURCE, oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True, whole451Accepted=False, wholeF03Accepted=False,
        newAccepted=0, formalUpdated=False, effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs), len(pending), len(ids-refs)) == (3353, 2492, 2894)
    return value

def documents(value, raw, snap):
    current = json.loads(raw)
    result = raw
    overlay = dict(source=SOURCE, manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
        sha256=data.sha((OUT/'manifest.json').read_bytes()), record=RECORD,
        qualification=value['currentMainRepositoryStaticContexts'], joinedContextWarnings=3353,
        currentWholeJoinPending=2492, sourceDerivedRaw=6247, totalPriorCorrections=3194,
        all995OldRuntimePreserved=True, newAccepted=0, formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name])
        assert 'repositoryResourcePG13640Overlay' not in section
        section['repositoryResourcePG13640Overlay'] = copy.deepcopy(overlay)
        result, _, _ = replaced(result, name, section)
    result_snap, _, _ = replaced(snap, 'inventorySha256', data.sha(result))
    validate_docs(result, result_snap, current, json.loads(snap))
    return result, result_snap
