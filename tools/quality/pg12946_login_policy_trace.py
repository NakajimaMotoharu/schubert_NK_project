"""Registry v2: current rows/counts only; old runtime domains retained by immutable reference."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced, SECTIONS, INV, SNAP
from pg9338_wbs_reference_metadata_post import validate

SOURCE = 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
OUT = data.BASE/'PG12946-login-policy-trace-v1'
POST = data.BASE/'PG12947-login-policy-trace-post-v1'
PRIOR_PATH = data.BASE/'PG12930-coordinator-trace-v1/manifest.json'
PRIOR_SHA = 'b984b53514914c24fde1c36eb638c660f5e1cf95ce0c2a819ec620eebb6045d3'
PROOF_SHA = 'a6d70118ffcbc9dc1ccbdf56e3ed711d1811561cc2043a1bf7a2af0ec771d426'
NEW = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginAttemptSequenceTest.java'
SPEC = 'evidence/01_PT/018_NK-OPS-001/2395_P007失敗窓時系列_単体テスト仕様書.md'
MARKER = 'previousLoginWindowPG12946Reference'

def inputs():
    prior = data.read_checked(PRIOR_PATH,PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG12938-login-policy-six-compile-v1/manifest.json','f65a05a93b6a857e21602222b5a9f5287a92b185cf6b540792c5bf8d7a10cac2')
    proof = data.read_checked(data.BASE/'PG12944-login-policy-post-v1/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG12936-login-policy-plan-v1/manifest.json','745d68510d587effc590ab73fce3db60fde883b7b518c6c69a361c93f06c67d2')
    assert normal['source'] == proof['source'] == plan['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == proof['actualExit'] == 0
    assert proof['selectedTwoMainCoverage100'] and proof['observedTestExecutions'] == 9 and proof['rawStatic'] == proof['staticGateExit'] == proof['spotbugsSixExit'] == 0
    assert proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1965 and proof['newTestPhysical'] == 1
    hashes = normal['begin']['inputHashes']
    assert len(prior['sourceRows']) == 985 and all(hashes[r['path']] == r['sha256'] for r in prior['sourceRows'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,plan,hashes,raw,snap

def new_row(plan,hashes,raw):
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    subjects = list(plan['eligibilityClosureSourceHashes'])
    assert len(subjects) == 2 and all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P007-01' for p in subjects)
    return dict(path=NEW,sha256=hashes[NEW],owner='WBS-P007-01',canonicalOwner='WBS-P007-01',canonicalCostOwner='WBS-P007-01',
        changeOwner='WBS-P007-01',basis='2395_SS314_5_INDEPENDENT_IMMUTABLE_LOGIN_WINDOW_TIME_VECTORS',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec=SPEC,
        methodTestIds=['PT-AUT-WINDOW-001','PT-AUT-WINDOW-002','PT-AUT-WINDOW-003','PT-AUT-WINDOW-004'],mainSourceSubjects=subjects,
        ownerProofManifest=str((data.BASE/'PG12944-login-policy-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF_SHA)

def validate_registry(value,prior,plan,hashes,raw):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == prior['sourceRows']+[new_row(plan,hashes,raw)]
    assert value['sourceCount'] == len(value['sourceRows']) == len({r['path'] for r in value['sourceRows']}) == 986
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8472 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['observedTestExecutions'] == 9 and value['currentQualification']['rawStaticScope'] == 0
    assert value['registered'] == 1811 and value['javaPaths'] == 1813

def main():
    invocation = capture(__file__); assert not OUT.exists()
    prior,proof,plan,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = prior['sourceRows']+[new_row(plan,hashes,raw)]
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & ({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1813 and len(registered) == 1811 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=986,registered=1811,javaPaths=1813,registeredMain=965,totalMain=965,registeredTest=846,totalTest=848,
        unregisteredJavaPaths=unknown,newPathsAdded=1,newTestPaths=[NEW],original985AllFieldsPreserved=True,
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=9,newTestIds=4,suites=2,
            selectedTwoMain=proof['selectedTwoMain'],selectedTwoMainCoverage100=True,rawStaticScope=0,spotbugsSixExit=0,
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1965,newTestPhysical=1,fullArtifactCoverage100=False),
        sourceDerivedRaw=8472,totalPriorCorrections=951,actualViolationCount=None,
        rawSameBasis='All original source inputs/1843Main/1965Test bytes unchanged; only new Test source, actual new four-file static0',
        previousGlobalRawReference=dict(path='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12928-coordinator-context-v1/manifest.json',sha256='9c8e7149fb87f628d3c37f217e66ddc5f4a0cec98a4f0326bfd17450e162705c',source=prior['source']),
        inheritedFlatScopeCountersCopied=False,oldRuntimeDomainsReachableViaImmutablePriorReference=True,
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    validate_registry(value,prior,plan,hashes,raw); verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',value); print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name]; assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2396_P007失敗窓時系列_実行結果.md',currentAddedTestPaths=[NEW])
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1813,registered=1811,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=848,registered=846,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=986,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def emit():
    _,_,_,_,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap = documents(raw,snap); patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,asnap)]:
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__); assert not POST.exists()
    prior,_,plan,hashes,raw,snap = inputs(); m = json.loads((OUT/'manifest.json').read_bytes())
    validate_registry(m,prior,plan,hashes,raw)
    actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actualraw,actualsnap,json.loads(raw),json.loads(snap))
    assert (actualraw,actualsnap) == documents(raw,snap)
    labels = []
    for label,change in [('owner',lambda v:v['sourceRows'][-1].update(canonicalOwner='WBS-F03')),
        ('old-hash',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('source',lambda v:v.update(source='0'*40)),
        ('acceptance',lambda v:v.update(newAccepted=1)),('legacy-runtime-transfer',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),
        ('raw',lambda v:v.update(sourceDerivedRaw=0))]:
        bad = copy.deepcopy(m); change(bad); assert bad != m
        try: validate_registry(bad,prior,plan,hashes,raw)
        except AssertionError: labels.append(label)
        else: raise AssertionError('wrong current domain/owner/count accepted')
    observed = audit(); assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,original985AllFieldsPreserved=True,newCanonicalOwner='WBS-P007-01',
        registered=1811,javaPaths=1813,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
