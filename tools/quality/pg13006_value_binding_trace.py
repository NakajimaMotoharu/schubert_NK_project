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

SOURCE = '94eeea264b449e5826f292c746a9cd4655b3122a'
OUT = data.BASE/'PG13006-value-binding-trace-v1'
POST = data.BASE/'PG13007-value-binding-trace-post-v1'
PRIOR_PATH = data.BASE/'PG12982-query-binding-trace-v1/manifest.json'
PRIOR_SHA = '762b25517af68a865010d85af878ebd2b601f0db23645e16fba8a865cf1bda7a'
PROOF_SHA = '3ea296e632ac9f8e2b9ae5824fb0637a8edf821d4c49bfa9140f476c5c22df85'
NEWS = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'+part+'/'+name+'.java' for part,name in [('media','MediaRequestDescriptorBindingTest'),('scenario','ScenarioScriptFileBindingTest')]]
SPEC = 'evidence/01_PT/018_NK-OPS-001/2401_P008P009独立値束縛_単体テスト仕様書.md'
MARKER = 'previousValueBindingPG13006Reference'

def inputs():
    prior = data.read_checked(PRIOR_PATH,PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG12998-value-binding-six-compile-v1/manifest.json','f391201e726c7e4ad28b86b4e8d5ef332e2c06cfdca02d4df05529f332f8e730')
    proof = data.read_checked(data.BASE/'PG13004-value-binding-post-v1/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG12996-value-binding-plan-v1/manifest.json','07fc9a45967a0da188eae4777f4b39c3627b88850754c818afb3092701b74386')
    assert normal['source'] == proof['source'] == plan['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == proof['actualExit'] == 0
    assert not proof['selectedMainCoverage100'] and proof['observedTestExecutions'] == 6 and proof['rawStatic'] == 0 and proof['staticGateExit'] == 0 and proof['spotbugsSixExit'] == 0
    assert proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1968 and proof['newTestPhysical'] == 2
    hashes = normal['begin']['inputHashes']
    assert len(prior['sourceRows']) == 988 and all(hashes[r['path']] == r['sha256'] for r in prior['sourceRows'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,plan,hashes,raw,snap

def new_rows(plan,hashes,raw):
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}; rows = []
    for path,owner,prefix,count in [(NEWS[0],'WBS-P009-01','PT-MED-BIND',4),(NEWS[1],'WBS-P008-01','PT-SCN-SCRIPTBIND',2)]:
        subjects = [p for p in plan['eligibilityClosureSourceHashes'] if ('/media/' in p) == ('/media/' in path)]
        assert len(subjects) == 1 and all(logical[p]['owner'] == logical[p]['costOwner'] == owner for p in subjects)
        rows.append(dict(path=path,sha256=hashes[path],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
            changeOwner=owner,basis='2401_DISTINCT_WHOLE_VALUE_DESCRIPTOR_OR_SCRIPT_ID_BINDING',
            ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
            actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
            currentSourcePtQualificationInferred=False,independentSpec=SPEC,
            methodTestIds=[prefix+str(i).zfill(3) for i in range(1,count+1)],mainSourceSubjects=subjects,
            ownerProofManifest=str((data.BASE/'PG13004-value-binding-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF_SHA))
    return rows

def validate_registry(value,prior,plan,hashes,raw):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == prior['sourceRows']+new_rows(plan,hashes,raw)
    assert value['sourceCount'] == len(value['sourceRows']) == len({r['path'] for r in value['sourceRows']}) == 990
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8474 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['observedTestExecutions'] == 6 and value['currentQualification']['rawStaticScope'] == 0
    assert value['registered'] == 1815 and value['javaPaths'] == 1817

def main():
    invocation = capture(__file__); assert not OUT.exists()
    prior,proof,plan,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = prior['sourceRows']+new_rows(plan,hashes,raw)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & ({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1817 and len(registered) == 1815 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR_PATH.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=990,registered=1815,javaPaths=1817,registeredMain=965,totalMain=965,registeredTest=850,totalTest=852,
        unregisteredJavaPaths=unknown,newPathsAdded=2,newTestPaths=NEWS,original988AllFieldsPreserved=True,
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=6,newTestIds=6,suites=2,
            selectedMain=proof['selectedMain'],selectedMainCoverage100=False,rawStaticScope=0,spotbugsSixExit=0,
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1968,newTestPhysical=2,fullArtifactCoverage100=False),
        sourceDerivedRaw=8474,totalPriorCorrections=951,actualViolationCount=None,
        rawDeltaBasis='All original source inputs/1843Main/1967Test bytes unchanged; new two Tests and support static0; prior global raw retained; no global correction/new finding',
        globalRawDerivationReference=dict(path='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12964-public-receipt-context-v1/manifest.json',sha256='955f91d7d397fc2588f214c6ef3c76abbdae7e7363a4e679159f6a76f4eb80d7',source='c1d9b6e4b27b236ed8b40724f0701d2a2216237b'),
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
            record='evidence/01_PT/018_NK-OPS-001/2402_P008P009独立値束縛_実行結果.md',currentAddedTestPaths=NEWS)
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1817,registered=1815,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=852,registered=850,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=990,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
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
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,original988AllFieldsPreserved=True,newCanonicalOwners=['WBS-P009-01','WBS-P008-01'],
        registered=1815,javaPaths=1817,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
