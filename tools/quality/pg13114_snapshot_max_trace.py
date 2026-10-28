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

SOURCE = '5c378e064f0f8a7366316d4afa28fbb2cd9cec81'
OUT = data.BASE/'PG13114-snapshot-max-trace-v1'
POST = data.BASE/'PG13115-snapshot-max-trace-post-v1'
PRIOR_PATH = data.BASE/'PG13086-monitor-test-trace-v1/manifest.json'
PRIOR_SHA = 'b816f79093abd3ca919909e236448cd5543e92ed824df302c82f4c7920870547'
PROOF_SHA = '2e506ef62e654842ad448b38aa0a61f90b26ebaa98e3b84f42df50d221f07c9d'
NEWS = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.java']
SPEC = 'evidence/01_PT/018_NK-OPS-001/2414_Scenario最大snapshot純memory_単体テスト仕様.md'
MARKER = 'previousScenarioSnapshotMaxPG13114Reference'

def inputs():
    prior = data.read_checked(PRIOR_PATH,PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG13106-snapshot-corrected-six-compile-v1/manifest.json','0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7')
    proof = data.read_checked(data.BASE/'PG13112-snapshot-corrected-post-v1/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG13104-snapshot-corrected-plan-v1/manifest.json','03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8')
    assert normal['source'] == proof['source'] == plan['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == proof['actualExit'] == 0
    assert not proof['selectedMainCoverage100'] and proof['observedTestExecutions'] == 6 and proof['rawStatic'] == 0 and proof['staticGateExit'] == 0 and proof['spotbugsSixExit'] == 0
    assert proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1968 and proof['newTestPhysical'] == 2
    hashes = normal['begin']['inputHashes']
    assert len(prior['sourceRows']) == 992 and all(hashes[r['path']] == r['sha256'] for r in prior['sourceRows'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,plan,hashes,raw,snap

def new_rows(plan,hashes,raw):
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    subjects = list(plan['eligibilityClosureSourceHashes']); assert len(subjects) == 1
    owner = 'WBS-P008-05'; assert logical[subjects[0]]['owner'] == logical[subjects[0]]['costOwner'] == owner
    return [dict(path=NEWS[0],sha256=hashes[NEWS[0]],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
        changeOwner=owner,basis='2414_DISTINCT_WHOLE_MAXIMUM_IMMUTABLE_PRE_IO_SNAPSHOT_ORACLES',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec=SPEC,
        methodTestIds=['PT-SCN-SNAPSHOTMAX-'+str(i).zfill(3) for i in range(1,4)],mainSourceSubjects=subjects,
        ownerProofManifest=str((data.BASE/'PG13112-snapshot-corrected-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF_SHA)]

def validate_registry(value,prior,plan,hashes,raw):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == prior['sourceRows']+new_rows(plan,hashes,raw)
    assert value['sourceCount'] == len(value['sourceRows']) == len({r['path'] for r in value['sourceRows']}) == 993
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8461 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['observedTestExecutions'] == 3 and value['currentQualification']['rawStaticScope'] == 0
    assert value['registered'] == 1818 and value['javaPaths'] == 1820

def main():
    invocation = capture(__file__); assert not OUT.exists()
    prior,proof,plan,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = prior['sourceRows']+new_rows(plan,hashes,raw)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & ({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1820 and len(registered) == 1818 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=993,registered=1818,javaPaths=1820,registeredMain=965,totalMain=965,registeredTest=853,totalTest=855,
        unregisteredJavaPaths=unknown,newPathsAdded=1,newTestPaths=NEWS,original992AllFieldsPreserved=True,
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=3,newTestIds=3,suites=1,
            selectedMain=proof['selectedMain'],selectedMainCoverage100=False,rawStaticScope=0,spotbugsSixExit=0,
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1972,newTestPhysical=1,fullArtifactCoverage100=False),
        sourceDerivedRaw=8461,totalPriorCorrections=964,actualViolationCount=None,
        rawDeltaBasis='All original source inputs/1843Main/1972Test bytes unchanged; new one corrected Test static0; prior8461/corr964 retained; new oracle correction is not an original baseline correction',
        globalRawDerivationReference=dict(path='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13084-monitor-test-context-v1/manifest.json',sha256='172f097d528028d906b5e012a43d413b067f5b0e4c360c8ce2163c0032328125',source='42ae92a74d57a9e1d031613d5b558af3ebe2925c'),
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
            record='evidence/01_PT/018_NK-OPS-001/2415_Scenario最大snapshot純memory_実行結果.md',currentAddedTestPaths=NEWS)
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1820,registered=1818,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=855,registered=853,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=993,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
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
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,original992AllFieldsPreserved=True,newCanonicalOwners=['WBS-P008-05'],
        registered=1818,javaPaths=1820,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
