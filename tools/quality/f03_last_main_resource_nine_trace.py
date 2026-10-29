"""Nine current Main resource ownership references; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_remaining_main_resource_six_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR = ('PG13968-main-resource-six-contracts-trace-v1','42f57b519157ab5439bfa4d25b41a756a0f6a5cffe43cd2dcc50880eef8a17d8')
REVIEW = ('PG13976-last-main-resource-nine-contracts-v1','2338005fed98d4313914b9959576fdc12ce8fd12ac244bf2deb67d937e322b84')
PROOF = ('PG13978-last-main-resource-nine-contracts-post-v1','7f33f861d77aec03aede02297f777d93dab42617a2202e6ca47b83102f119049')
OUT = data.BASE/'PG13980-last-main-resource-nine-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2550_Main資源残九指摘_公開source所有点検結果.md'
NEW_IDS = {'PMD-02845','PMD-02846','PMD-02856','PMD-02918','PMD-03027','PMD-03044','PMD-03045','PMD-03102','PMD-03103'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3407,2546)
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
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '28f97b1577fd937aa92277413bab17dd1385b40a'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == 'b2826c0b2a5742d1a65069d9057452159894ea138431f0fc18248fdfb0df826f'
    assert data.sha(snap) == '1b08e1ef6d92a3702f1c42ca3211e6a74434f4d56ca507cc412d6b61e14316b6'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentLastMainResourceNineReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=9,newCurrentReferences=9,rawRetained=9,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allNineAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3416,2555,2831)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentLastMainResourceNineReferences'],joinedContextWarnings=3416,currentWholeJoinPending=2555,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=9,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'lastMainResourceNinePG13980Overlay' not in section
        section['lastMainResourceNinePG13980Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
