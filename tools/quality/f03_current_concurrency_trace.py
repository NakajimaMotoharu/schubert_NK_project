"""Five previously reviewed exact-source references; no diagnostic removal or new runtime."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_repository_resource_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
PRIOR = ('PG13640-repository-resource-trace-v1','25fe7097e595fb9899af0f981d61f7e275dfd50b2c4c692e7bfafd5cd09719c5')
REVIEW = ('PG13703-current-concurrency-reason-join-recovery-v1','637d3ce581ffc589ea0519e77a1f37a5f1946dcf1070f61ebecb3132b99d98a4')
PROOF = ('PG13704-current-concurrency-reason-join-post-v1','97d17086b4f150a57c5fde59e1f9f23057860ee6f9f98734ec9847a9b5c5427c')
OUT = data.BASE/'PG13706-current-concurrency-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2500_Main親同期・表示volatile五理由_現集合結合結果.md'
NEW_IDS = {'PMD-00131','PMD-00132','PMD-00133','PMD-00134','PMD-07317'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3353,2492)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == proof['newReasons'] == 0
    assert proof['sourceContexts'] == proof['reusedReasons'] == 5 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '9f43e1a753ac2dd219e8b2441c86d04d9ca29731'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == '3eff42a66975859283f7f39491d1b043f801a456fc1ff2f30462cdde5e596abd'
    assert data.sha(snap) == '35195fabb84427b9fd79c9c07f0b55de615d97225efd99ab1fe6a4bcd8856d25'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentExistingConcurrencyReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=0,reusedReasons=5,newCurrentReferences=5,rawRetained=5,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allFiveAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3358,2497,2889)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentExistingConcurrencyReferences'],joinedContextWarnings=3358,currentWholeJoinPending=2497,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=0,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'concurrencyReasonPG13706Overlay' not in section
        section['concurrencyReasonPG13706Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
