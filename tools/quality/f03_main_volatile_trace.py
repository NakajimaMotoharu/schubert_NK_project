"""Nine current field-visibility references; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_current_concurrency_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
PRIOR = ('PG13706-current-concurrency-trace-v1','313577daeb7cae8d24f9efb7420860d8b8fca4468e5a0088b9bdd3af63c8a1b9')
REVIEW = ('PG13714-main-nine-volatile-contexts-v1','d452722d17ee6449bba56233503d5311629cea47911b904e7fe33259ae74d1dc')
PROOF = ('PG13716-main-nine-volatile-post-v1','16c89e1e1f3c1f2dcc2bf0e195f69fa1f73846b41b0b436230b43c4c32f3de8d')
OUT = data.BASE/'PG13718-main-volatile-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2502_Main残volatile九_個別契約点検結果.md'
NEW_IDS = {'PMD-07226','PMD-07249','PMD-07250','PMD-07251','PMD-07252','PMD-07253','PMD-07303','PMD-07329','PMD-07330'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3358,2497)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 9 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '2523453f3e0cf3716d437f3cd26a2444fba4d081'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == '1fb7c70c484e88092a6905efaccf258b7c4503983fc93c88783596bede7d92ee'
    assert data.sha(snap) == '1bdaa3941fa67fd92c34db5e929639f4a3637530812999091227c941c69b71e7'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentMainVolatileReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=9,newCurrentReferences=9,rawRetained=9,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allNineAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3367,2506,2880)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentMainVolatileReferences'],joinedContextWarnings=3367,currentWholeJoinPending=2506,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=9,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'volatilePG13718Overlay' not in section
        section['volatilePG13718Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
