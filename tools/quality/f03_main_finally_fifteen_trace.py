"""Fifteen current finally contract references; no diagnostic removal or graph/runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_main_resource_six_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
PRIOR = ('PG13752-main-resource-six-trace-v1','e5fd3d83e849f6113c6a15590e613ccfb7d63601a2b9a6aa6b71ea37abf9fd01')
REVIEW = ('PG13760-main-finally-fifteen-contexts-v1','26926a5a3246ae255c43c575303b7b4735eb1408392a75cd7ceda1720fce5c41')
PROOF = ('PG13762-main-finally-fifteen-post-v1','31e607c23aca4e1ebb854a8d1b03e1fce9d5e968bcdd3b4b60c1aa53c3339b2d')
OUT = data.BASE/'PG13764-main-finally-fifteen-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2512_Main残finally十五_個別順位点検結果.md'
NEW_IDS = {'PMD-00104','PMD-00111','PMD-03264','PMD-03269','PMD-03274','PMD-03279','PMD-03348','PMD-03353','PMD-07190','PMD-07197','PMD-07345','PMD-07389','PMD-07394','PMD-07399','PMD-07408'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3373,2512)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 15 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '3368d2ac323c7806b2194f00f7a3816b83b1d45e'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == 'a6ace69786f72c6656efe611457cb401cdabf276926829b58f51bd5f093fed15'
    assert data.sha(snap) == 'b2d9183b4be8884984afc6af61d3d969c6b928eace373d962016d93e3204b660'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentFinallyFifteenReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=15,newCurrentReferences=15,rawRetained=15,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allFifteenAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3388,2527,2859)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentFinallyFifteenReferences'],joinedContextWarnings=3388,currentWholeJoinPending=2527,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=15,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'finallyFifteenPG13764Overlay' not in section
        section['finallyFifteenPG13764Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
