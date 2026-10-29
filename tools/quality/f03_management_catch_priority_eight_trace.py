"""Eight raw management type-priority references, four spans/two clauses; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_last_main_resource_nine_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR = ('PG13980-last-main-resource-nine-trace-v1','456bae0fe833fa596971b8c746e96e80eb492a462108cac28048deff25a812df')
REVIEW = ('PG13988-management-catch-priority-eight-contexts-v1','7050701b1ef8c820874d4ca9482ee0e6d487c3336f95aaed05a5d8aa5823784f')
PROOF = ('PG13990-management-catch-priority-eight-post-v1','01a2ceea12a7ea270bdfab5317294877ae37b0150513e1f529ffdad0781ecd8e')
OUT = data.BASE/'PG13992-management-catch-priority-eight-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2552_管理HTTP例外順位八raw指摘_静的点検結果.md'
NEW_IDS = {'PMD-00073','PMD-00074','PMD-00075','PMD-00076','PMD-07231','PMD-07232','PMD-07233','PMD-07234'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3416,2555)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 8 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '928444e8a43b1d3668fe48a399e1fcfbeefc0457'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == 'f95d5c5321a47dad1748b466abc53745b250adf7612adac56cfddccef9f569fb'
    assert data.sha(snap) == '0ad25559d8fbee836cf1c37d6d719774267c3ffe4d063c6736921410ee9b9c2a'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentManagementCatchPriorityEightReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasonRows=8,uniqueOperandSpans=4,uniqueCatchClauses=2,newCurrentReferences=8,rawRetained=8,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allEightAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3424,2563,2823)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentManagementCatchPriorityEightReferences'],joinedContextWarnings=3424,currentWholeJoinPending=2563,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=8,uniqueOperandSpans=4,uniqueCatchClauses=2,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'managementCatchPriorityEightPG13992Overlay' not in section
        section['managementCatchPriorityEightPG13992Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
