"""Seven current Web resource ownership references; no diagnostic removal or runtime qualification."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_snapshot_program_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR = ('PG13846-snapshot-program-trace-v1','f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107')
REVIEW = ('PG13944-web-startup-resource-seven-contexts-v1','1fb8cab21721034d0a0fc7952ac4a7a00b58399b84cea34e8b2d7e95ddd27682')
PROOF = ('PG13946-web-startup-resource-seven-post-v1','839e5ce3c7bc813652b22798f2ba5310ebc093df70192bc051f4fbeb110e22d5')
OUT = data.BASE/'PG13948-web-startup-resource-seven-trace-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2545_Web起動資源七指摘_個別所有契約点検結果.md'
NEW_IDS = {'PMD-07209','PMD-07255','PMD-07256','PMD-07257','PMD-07258','PMD-07259','PMD-07260'}

def state_after():
    ids,refs,pending = previous_state()
    assert NEW_IDS <= ids-refs and (len(ids),len(refs),len(pending)) == (6247,3394,2533)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    review = data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    rows = data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    assert prior['source'] == review['source'] == proof['source'] == SOURCE
    assert review['actualExit'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['sourceContexts'] == 7 and proof['reviewManifestSha256'] == REVIEW[1]
    assert {r['id'] for r in rows} == NEW_IDS and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in rows)
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows']) == 995 and all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base = '34aa7a65535879d234962b5497fc7f5ec0c38e46'
    raw,snap = [subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == '2e7740f742ea117c364acb981423a40e31d304adc3b10304ebf20ec993656b0b'
    assert data.sha(snap) == '29738f891143f5f943bc3ad22e8cba96095fe2e670ef4ab12e397a9c6a3f3ccb'
    return prior,rows,raw,snap

def expected(prior,rows):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        currentWebStartupResourceSevenReferences=dict(reviewManifestSha256=REVIEW[1],proofManifestSha256=PROOF[1],source=SOURCE,rows=rows,newSourceReasons=7,newCurrentReferences=7,rawRetained=7,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allSevenAddedToGlobalJoinPending=True),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
        all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs)) == (3401,2540,2846)
    return value

def documents(value,raw,snap):
    current = json.loads(raw);result = raw
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
        qualification=value['currentWebStartupResourceSevenReferences'],joinedContextWarnings=3401,currentWholeJoinPending=2540,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasons=7,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section = copy.deepcopy(current[name]);assert 'webStartupResourceSevenPG13948Overlay' not in section
        section['webStartupResourceSevenPG13948Overlay'] = copy.deepcopy(overlay);result,_,_ = replaced(result,name,section)
    result_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
