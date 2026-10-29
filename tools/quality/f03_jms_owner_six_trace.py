"""Six current JMS owner transfer references; no provider/graph/runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_main_finally_fifteen_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
PRIOR = ('PG13764-main-finally-fifteen-trace-v1','87e71ae3e41ae9bf408bec0f1a90fb39716abe9a83b969c00a0e97fba5e446c6')
REVIEW = ('PG13773-jms-owner-six-contexts-recovery-v1','c2dfafc531151efaa2d8c36fb59da12137e8fc4578b9f522812cdaf7e260d815')
PROOF = ('PG13774-jms-owner-six-post-v1','2a390dc4d645e542c3cb577da625bf1c188773d3c915866131082321c5491b11')
OUT = data.BASE/'PG13776-jms-owner-six-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2514_JMS長寿命owner六箇所_現source点検結果.md'
NEW_IDS = {'PMD-00156','PMD-00157','PMD-00158','PMD-07337','PMD-07338','PMD-07357'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3388,2527)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 6 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '866ccf74e7cc6c35beeacf1c4b09bf178b189d7c'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == '730a7715a9565d44f56598b099589dddbc55261157ea24126ae98a4d8fdac83b'
    assert data.sha(snap) == '9a4c9b7a41f1e71a527d9c32d2f30f7764f24309b158cfb71e170f9a29bd5e68'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentJmsOwnerSixReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=None,reviewedCurrentReasons=6,firstEverReasonCountUnproven=True,newCurrentReferences=6,rawRetained=6,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allSixAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3394,2533,2853)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentJmsOwnerSixReferences'],joinedContextWarnings=3394,currentWholeJoinPending=2533,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=None,reviewedCurrentReasons=6,firstEverReasonCountUnproven=True,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'jmsOwnerSixPG13776Overlay' not in section
        section['jmsOwnerSixPG13776Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
