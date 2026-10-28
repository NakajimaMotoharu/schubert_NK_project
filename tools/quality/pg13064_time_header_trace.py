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

SOURCE = '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
OUT = data.BASE/'PG13064-time-header-trace-v1'
POST = data.BASE/'PG13065-time-header-trace-post-v1'
PRIOR_PATH = data.BASE/'PG13028-http-route-name-trace-v1/manifest.json'
PRIOR_SHA = '8cc4b73e1470a67b8e458abb89afb2284cc34fe8c5a3660f57dd16e339e41637'
PROOF_SHA = 'b40146077c160e89ae69a0f370440040422174f2d24c4a2050f9da7cb5934bbd'
NEWS = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionCommandTimeBoundaryTest.java', 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/ContentDispositionBoundaryTest.java']
SPEC = 'evidence/01_PT/018_NK-OPS-001/2410_業務時刻・媒体header境界6_単体テスト仕様.md'
MARKER = 'previousTimeHeaderBoundaryPG13064Reference'

def inputs():
    prior = data.read_checked(PRIOR_PATH,PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json','fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    proof = data.read_checked(data.BASE/'PG13062-time-header-post-v1/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG13054-time-header-plan-v1/manifest.json','2088beba343b5c547520d3c55fa3cc6cc1e286319df6a4f60606d2e8cff6df13')
    assert normal['source'] == proof['source'] == plan['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == proof['actualExit'] == 0
    assert not proof['selectedMainCoverage100'] and proof['observedTestExecutions'] == 6 and proof['rawStatic'] == 0 and proof['staticGateExit'] == 0 and proof['spotbugsSixExit'] == 0
    assert proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1970 and proof['newTestPhysical'] == 2
    hashes = normal['begin']['inputHashes']
    assert len(prior['sourceRows']) == 990 and all(hashes[r['path']] == r['sha256'] for r in prior['sourceRows'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,plan,hashes,raw,snap

def new_rows(plan,hashes,raw):
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}; rows = []
    for path,owner,prefix,subject in [(NEWS[0],'WBS-P011-03','PT-CMD-TIMEBOUND','QuestionCommandMetadata.java'),(NEWS[1],'WBS-P009-04','PT-MED-HEADERBOUND','ContentDispositionFactory.java')]:
        subjects = [p for p in plan['eligibilityClosureSourceHashes'] if p.endswith('/'+subject)]
        assert len(subjects) == 1 and all(logical[p]['owner'] == logical[p]['costOwner'] == owner for p in subjects)
        rows.append(dict(path=path,sha256=hashes[path],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
            changeOwner=owner,basis='2410_DISTINCT_WHOLE_UTC_TIME_OR_UTF8_HEADER_BOUNDARY_ORACLES',
            ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
            actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
            currentSourcePtQualificationInferred=False,independentSpec=SPEC,
            methodTestIds=[prefix+'-'+str(i).zfill(3) for i in range(1,4)],mainSourceSubjects=subjects,
            ownerProofManifest=str((data.BASE/'PG13062-time-header-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF_SHA))
    return rows

def validate_registry(value,prior,plan,hashes,raw):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == prior['sourceRows']+new_rows(plan,hashes,raw)
    assert value['sourceCount'] == len(value['sourceRows']) == len({r['path'] for r in value['sourceRows']}) == 992
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8472 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['observedTestExecutions'] == 6 and value['currentQualification']['rawStaticScope'] == 0
    assert value['registered'] == 1817 and value['javaPaths'] == 1819

def main():
    invocation = capture(__file__); assert not OUT.exists()
    prior,proof,plan,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = prior['sourceRows']+new_rows(plan,hashes,raw)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & ({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1819 and len(registered) == 1817 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=992,registered=1817,javaPaths=1819,registeredMain=965,totalMain=965,registeredTest=852,totalTest=854,
        unregisteredJavaPaths=unknown,newPathsAdded=2,newTestPaths=NEWS,original990AllFieldsPreserved=True,
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=6,newTestIds=6,suites=2,
            selectedMain=proof['selectedMain'],selectedMainCoverage100=False,rawStaticScope=0,spotbugsSixExit=0,
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1970,newTestPhysical=2,fullArtifactCoverage100=False),
        sourceDerivedRaw=8472,totalPriorCorrections=953,actualViolationCount=None,
        rawDeltaBasis='All original source inputs/1843Main/1970Test bytes unchanged; new two Tests static0; prior raw8472/corr953 retained; no global correction/new finding',
        globalRawDerivationReference=dict(path='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13026-http-route-name-context-v1/manifest.json',sha256='e9a90bad3af371bf236ab3a54a29a5d6ea852038514195177a939dc93c4c46b1',source='2f4290e7e511ea30224d087f78d44964d3488919'),
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
            record='evidence/01_PT/018_NK-OPS-001/2411_業務時刻・媒体header境界6_実行結果.md',currentAddedTestPaths=NEWS)
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1819,registered=1817,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=854,registered=852,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=992,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
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
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,original990AllFieldsPreserved=True,newCanonicalOwners=['WBS-P011-03','WBS-P009-04'],
        registered=1817,javaPaths=1819,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
