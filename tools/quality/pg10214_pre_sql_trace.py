"""Add three explicit Test bindings; preserve all prior fields/history, costs and acceptance."""
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
BASE='cce6e64be'
SOURCE='d4ba0fcbe8855b9674413d395b46d2de7bb2ded9'
PRIOR='376ee1a844a20c775780634c6b8a72daf2c651caf016171ae30ec4e7363f3e92'
PROOF='69ad4f6834f20955c7bf1b76609c5960c3eab0dd2b0d3fa7f2ce54c93f9fb21b'
PMO='documents/400_PGPT/470_PMO/'
INV,SNAP=PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT=data.BASE/'PG10214-pre-sql-trace-v1'
POST=data.BASE/'PG10216-pre-sql-trace-post-v1'
SECTIONS=('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior=data.read_checked(data.BASE/'PG10180-oracle-batch-trace-v1/manifest.json',PRIOR)
    proof=data.read_checked(data.BASE/'PG10208-pre-sql-boundary-post-v1/manifest.json',PROOF)
    prepared=data.read_checked(data.BASE/'PG10204-pre-sql-boundary-preflight-v1/manifest.json',
        '2ff834c4411928d402f0cdc1f67aa579edca4d6bf6566cd256c82623df55502c')
    cases=data.read_checked(data.BASE/'PG10204-pre-sql-boundary-preflight-v1/cases.json',prepared['casesSha256'])
    assert proof['actualExit']==0 and proof['source']==SOURCE and (proof['tests'],proof['newTestIds'])==(13,13)
    assert all(data.sha((ROOT/p).read_bytes())==h for p,h in prepared['allCurrentSourceInputHashes'].items())
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,prepared,cases,raw,snap


def expected(prior,prepared,cases,raw):
    rows=copy.deepcopy(prior['sourceRows'])
    assert len(rows)==976
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
            basis='EXPLICIT_ADM083_QRY007_AND_ORIGINAL_REPOSITORY_LOGICAL_OWNER',
            ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',actualAllocatedPp=None,
            additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
            independentSpec=('evidence/01_PT/014_NK-QRY-001/007_NK-QRY-001_SQL前境界単体仕様.md'
                if 'QuestionQuery' in path else 'evidence/01_PT/010_NK-ADM-001/083_NK-ADM-001_SQL前null・権限境界単体仕様.md'),
            methodTestIds=[r['testId'] for r in selected],mainSourceSubjects=[repository],
            historicalLogicalMainSha256=logical[repository]['sha256'],currentMainSourceSha256=current_main_sha,
            currentMainPhysicalSha256=prepared['physicalMainClasses'][physical],historicalLogicalShaReassigned=False,
            sourceSpecificRuntimeProof=dict(source=SOURCE,manifest=str((data.BASE/'PG10208-pre-sql-boundary-post-v1/manifest.json').relative_to(ROOT)),
                sha256=PROOF,tests=13,suites=3,programMethodCount=len(selected),newProgramTestIds=len(selected),
                sharedRunReferenceNotAdditive=True,wholeClassFour100=False,historicalProofReassigned=False)))
    assert rows[:976]==prior['sourceRows'] and len(rows)==979
    hashes=prepared['allCurrentSourceInputHashes']
    universe={p for p in hashes if '/java/' in p and p.endswith('.java')}
    unknown=sorted(universe-(set(logical)|{r['path'] for r in rows}))
    assert len(universe)==1806 and unknown==prior['unregisteredJavaPaths'] and len(unknown)==2
    kept={k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=new,newPathsAdded=3,
        newLogicalCandidates=prior['newLogicalCandidates']+3,javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=965,totalMain=965,registeredTest=839,totalTest=841,unregisteredJavaPaths=unknown,
        allPrior976RowsUnchanged=True,newMethodIds=13,productTestsExecuted=0,newAccepted=0,formalUpdated=False,
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
        assert 'previousPreSqlBoundaryRegistryReference' not in section
        section['previousPreSqlBoundaryRegistryReference']={k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2037_SQL前境界三Test追跡結果.md',
            currentAddedTestPaths=value['newTestPaths'])
        if name==SECTIONS[0]:
            section.update(javaPaths=1806,registered=1804,unregistered=2,
                main=dict(total=965,registered=965,unregistered=0),test=dict(total=841,registered=839,unregistered=2),
                independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(sourceRows=979,newLogicalCandidates=971,
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
        metadataNegativeVectors=vectors,registered=1804,total=1806,unknown=2,allPrior976RowsUnchanged=True,
        originalBudgetAndAcceptanceUnchanged=True,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic; this immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
