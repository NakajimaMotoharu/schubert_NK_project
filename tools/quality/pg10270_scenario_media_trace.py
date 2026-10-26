"""Add two explicit Test bindings and derive counters; preserve prior fields, costs and acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate

ROOT=data.ROOT
BASE='270d87b5c'
SOURCE='f12718441140c670950760185b596ab5627377db'
PRIOR='13346b8b4cdf5158d37cc4e61971af2fd41f0de32fc5f0a8a4d8b13bf0ec0077'
PROOF='d0f678a7623728bf03bdcff2628ad69d6ad12797bc2a00df35b9bf38a98750ed'
PMO='documents/400_PGPT/470_PMO/'
INV,SNAP=PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT=data.BASE/'PG10270-scenario-media-trace-v1'
POST=data.BASE/'PG10272-scenario-media-trace-post-v1'
SECTIONS=('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior=data.read_checked(data.BASE/'PG10243-header-oracle-trace-v2/manifest.json',PRIOR)
    proof=data.read_checked(data.BASE/'PG10266-scenario-media-boundary-post-v1/manifest.json',PROOF)
    prepared=data.read_checked(data.BASE/'PG10262-scenario-media-boundary-preflight-v1/manifest.json',
        'b754c6de3bf345c52acbc1788ee66bc05ae5deb6956a721b610968097f4faf72')
    cases=data.read_checked(data.BASE/'PG10262-scenario-media-boundary-preflight-v1/cases.json',prepared['casesSha256'])
    assert proof['actualExit']==0 and proof['source']==SOURCE and (proof['tests'],proof['newTestIds'])==(22,22)
    assert all(data.sha((ROOT/p).read_bytes())==h for p,h in prepared['allCurrentSourceInputHashes'].items())
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,prepared,cases,raw,snap


def expected(prior,prepared,cases,raw):
    rows=copy.deepcopy(prior['sourceRows'])
    assert len(rows)==979
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    assert len(logical)==941
    new=[]
    for path in sorted(prepared['newSourceHashes']):
        selected=[r for r in cases if r['path']==path]
        owner=selected[0]['canonicalOwner']
        assert all(r['canonicalOwner']==owner for r in selected)
        repository=path.replace('/test/','/main/').replace('PreSqlBoundaryTest.java','Repository.java')
        assert logical[repository]['owner']==logical[repository]['costOwner']==owner
        current_main_sha=prepared['allCurrentSourceInputHashes'][repository]
        assert data.sha((ROOT/repository).read_bytes())==current_main_sha
        physical=repository.split('/java/',1)[1].removesuffix('.java')+'.class'
        assert physical in prepared['physicalMainClasses']
        assert path not in {r['path'] for r in rows}
        new.append(path)
        rows.append(dict(path=path,sha256=prepared['newSourceHashes'][path],owner=owner,
            canonicalOwner=owner,canonicalCostOwner=owner,changeOwner='WBS-G13.07',legacyReportedOwner=None,
            basis='EXPLICIT_SCN005_MED003_AND_ORIGINAL_REPOSITORY_LOGICAL_OWNER',
            ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',actualAllocatedPp=None,
            additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
            independentSpec=('evidence/01_PT/008_NK-SCN-001/005_NK-SCN-001_SQL前入力境界単体仕様.md'
                if 'ScenarioPreSql' in path else 'evidence/01_PT/009_NK-MED-001/003_NK-MED-001_SQL前入力境界単体仕様.md'),
            methodTestIds=[r['testId'] for r in selected],mainSourceSubjects=[repository],
            historicalLogicalMainSha256=logical[repository]['sha256'],currentMainSourceSha256=current_main_sha,
            currentMainPhysicalSha256=prepared['physicalMainClasses'][physical],historicalLogicalShaReassigned=False,
            sourceSpecificRuntimeProof=dict(source=SOURCE,manifest=str((data.BASE/'PG10266-scenario-media-boundary-post-v1/manifest.json').relative_to(ROOT)),
                sha256=PROOF,tests=len(cases),suites=len({r['className'] for r in cases}),programMethodCount=len(selected),newProgramTestIds=len(selected),
                sharedRunReferenceNotAdditive=True,wholeClassFour100=False,historicalProofReassigned=False)))
    assert rows[:len(prior['sourceRows'])]==prior['sourceRows'] and len(rows)==981 and len(new)==2
    hashes=prepared['allCurrentSourceInputHashes']
    universe={p for p in hashes if '/java/' in p and p.endswith('.java')}
    unknown=sorted(universe-(set(logical)|{r['path'] for r in rows}))
    assert len(universe)==1808 and unknown==prior['unregisteredJavaPaths'] and len(unknown)==2
    known=set(logical)|{r['path'] for r in rows}
    mains={p for p in universe if '/src/main/java/' in p}
    tests=universe-mains
    old_legacy=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in prior['sourceRows'])
    assert old_legacy==745
    kept={k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=new,newPathsAdded=len(new),
        newLogicalCandidates=prior['newLogicalCandidates']+len(new),javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=len(mains&known),totalMain=len(mains),registeredTest=len(tests&known),totalTest=len(tests),unregisteredJavaPaths=unknown,
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        priorActualLegacyOwnerLabelsDifferingFromCanonical=old_legacy,
        priorRecordedLegacyOwnerLabelsDifferingFromCanonical=json.loads(raw)[SECTIONS[1]]['legacyOwnerLabelsDifferingFromCanonical'],
        allPrior979RowsUnchanged=True,newMethodIds=len(cases),productTestsExecuted=0,newAccepted=0,formalUpdated=False,
        effortPercent=None,**kept)


def contract(value,reference):
    if {k:value[k] for k in reference}!=reference:
        raise ValueError('exact source/owner/cost/runtime/history and UNKNOWN required')


def documents(raw,snap):
    value=json.loads((OUT/'manifest.json').read_bytes())
    pairs=[]
    for name in SECTIONS:
        section=json.loads(raw)[name]
        keys=('source','manifest','sha256','record','currentAddedTestPaths')
        assert 'previousScenarioMediaBoundaryRegistryReference' not in section
        section['previousScenarioMediaBoundaryRegistryReference']={k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2045_ScenarioMedia二Test追跡結果.md',
            currentAddedTestPaths=value['newTestPaths'])
        if name==SECTIONS[0]:
            section.update(javaPaths=value['javaPaths'],registered=value['registered'],unregistered=len(value['unregisteredJavaPaths']),
                main=dict(total=value['totalMain'],registered=value['registeredMain'],unregistered=value['totalMain']-value['registeredMain']),
                test=dict(total=value['totalTest'],registered=value['registeredTest'],unregistered=value['totalTest']-value['registeredTest']),
                independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(sourceRows=value['sourceCount'],newLogicalCandidates=value['newLogicalCandidates'],
                legacyOwnerLabelsDifferingFromCanonical=value['legacyOwnerLabelsDifferingFromCanonical'],
                guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        raw,before,after=replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after=replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    prior,prepared,cases,raw,snap=inputs()
    assert (ROOT/INV).read_bytes()==raw and (ROOT/SNAP).read_bytes()==snap
    result=expected(prior,prepared,cases,raw)
    observed=audit()
    assert observed['actualExit']==1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,wholeWbsAuditBefore=observed,**result))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap=inputs()
    assert (ROOT/INV).read_bytes()==raw and (ROOT/SNAP).read_bytes()==snap
    _,_,pairs,spairs=documents(raw,snap)
    patch='*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch+='*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines: patch+='@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation=capture(Path(__file__))
    assert not POST.exists()
    prior,prepared,cases,raw,snap=inputs()
    value=json.loads((OUT/'manifest.json').read_bytes())
    reference=expected(prior,prepared,cases,raw)
    contract(value,reference)
    after,asnap,_,_=documents(raw,snap)
    assert (ROOT/INV).read_bytes()==after and (ROOT/SNAP).read_bytes()==asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    vectors=[]
    for label,edit in (
        ('old-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='UNKNOWN')),
        ('new-cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-G13.07')),
        ('new-hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('current-main-hash',lambda v:v['sourceRows'][-1].update(currentMainSourceSha256='0'*64)),
        ('historical-main-hash',lambda v:v['sourceRows'][-1].update(historicalLogicalMainSha256='0'*64)),
        ('runtime-source',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(source=prior['source'])),
        ('program-count',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(programMethodCount=13)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('legacy-counter',lambda v:v.update(legacyOwnerLabelsDifferingFromCanonical=742)),
        ('registered-counter',lambda v:v.update(registered=0)),
        ('acceptance',lambda v:v.update(newAccepted=1))):
        changed=copy.deepcopy(reference)
        edit(changed)
        try: contract(changed,reference)
        except ValueError: vectors.append(label)
        else: raise AssertionError('invalid metadata accepted')
    observed=audit()
    assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=vectors,registered=value['registered'],total=value['javaPaths'],unknown=len(value['unregisteredJavaPaths']),allPrior979RowsUnchanged=True,
        legacyCounterBeforeRecorded=742,legacyCounterBeforeActual=745,legacyCounterCurrent=value['legacyOwnerLabelsDifferingFromCanonical'],
        originalBudgetAndAcceptanceUnchanged=True,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic; this immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
