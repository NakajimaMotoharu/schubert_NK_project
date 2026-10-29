"""Two bounded raw type references, one verified no-escape prefix only; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_main_type_priority_fifty_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR = ('PG14032-main-type-priority-fifty-trace-v1','00e70a07521d68dbaa468b00f5fb927afc2a01675699b0e3d176b9d624b88cd3')
REVIEW = ('PG14040-last-main-type-two-bounded-references-v1','e8c5e0c68bec62316a450966069f70e141ebf9d6a2fbaaddf36afd2aa71cd6c7')
PROOF = ('PG14042-last-main-type-two-bounded-post-v1','24fcea5f81ca2b4d178b4b18be989d199034c1e4d002391c25d475314469c964')
OUT = data.BASE/'PG14044-last-main-type-two-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2562_最後Main型判定二件_限定source参照結果.md'
NEW_IDS = {'PMD-00048','PMD-02778'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3491,2630)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    assert len({PRIOR[0],REVIEW[0],PROOF[0],OUT.name}) == 4
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 2 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '7b9d73bbbba774eef832db0f6ad4ec82724d3eaa'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == 'f2ac41a15f565c225d5fd809cdc9e0e2e31b9ffe5f65bb2f34901acfbd9f314f'
    assert data.sha(snap) == 'a361a94f5f92afcad4c3c0e3d69b300337048ae63935ddfed45e24f81bd8be5e'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentLastMainTypeTwoReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasonRows=2,uniqueOperandSpans=2,uniqueCatchClauses=2,newCurrentReferences=2,rawRetained=2,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allTwoAddedToGlobalJoinPending=True,selectedQuestionSpanPrefixOnly=True,wholeJavaUnicodeTranslationValidated=False),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3493,2632,2754)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentLastMainTypeTwoReferences'],joinedContextWarnings=3493,currentWholeJoinPending=2632,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=2,uniqueOperandSpans=2,uniqueCatchClauses=2,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'lastMainTypeTwoPG14044Overlay' not in section
        section['lastMainTypeTwoPG14044Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
