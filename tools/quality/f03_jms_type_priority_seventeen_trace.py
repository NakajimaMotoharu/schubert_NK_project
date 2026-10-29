"""Seventeen JMS type-priority references, twelve spans/nine clauses; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_management_catch_priority_eight_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR = ('PG14004-jms-type-priority-seventeen-trace-v1','9853831cafb7dc536ca1f5c74188ad0dc2fef552f39bee4b580738b23a8a761b')
REVIEW = ('PG14000-jms-type-priority-seventeen-contexts-v1','db1b067e3924d9cb775c38ab1a2023c43d34c254dd401ed0b602da1ed180b145')
PROOF = ('PG14002-jms-type-priority-seventeen-post-v1','e5373c0b17c92d208635eabd21002fd5ea6d42643db60af4ce4b8dc2bc4494c2')
OUT = data.BASE/'PG14004-jms-type-priority-seventeen-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2554_JMS例外順位十七raw指摘_静的点検結果.md'
NEW_IDS = {'PMD-00168','PMD-00173','PMD-00174','PMD-00175','PMD-00176','PMD-07355','PMD-00305','PMD-00306','PMD-07362','PMD-07363','PMD-07364','PMD-07365','PMD-07370','PMD-07283','PMD-07284','PMD-07289','PMD-07299'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3424,2563)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 17 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '3ba2eca6135108c7b44d48fe5217a2856d2c1f00'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == '7f2b1eade7e384389b24fb7f9c0d7492d76bd978d215a89069f5697c44d87f18'
    assert data.sha(snap) == '4c2b43025043df4b3200ecd4ec5907519ed3233a0ad116ddd655f1a9c2338f95'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentJmsTypePrioritySeventeenReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasonRows=17,uniqueOperandSpans=12,uniqueCatchClauses=9,newCurrentReferences=17,rawRetained=17,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allSeventeenAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3441,2580,2806)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentJmsTypePrioritySeventeenReferences'],joinedContextWarnings=3441,currentWholeJoinPending=2580,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=17,uniqueOperandSpans=12,uniqueCatchClauses=9,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'jmsTypePrioritySeventeenPG14004Overlay' not in section
        section['jmsTypePrioritySeventeenPG14004Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
