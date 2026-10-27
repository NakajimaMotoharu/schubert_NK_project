"""API-Web scrape fixture current28 and source owner/cost binding; whole quality remains HOLD."""
import copy
import difflib
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
BASE = '1be156b6ebb139713db31a561b8b024972975471'
OUT = data.BASE/'PG12418-batch-runtime-trace-v1'
POST = data.BASE/'PG12420-batch-runtime-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12390-pool-batch-trace-v1/manifest.json',
        'b2481b73b8a2da895ef7e3eca042a82a8d0ca975bbab0eebd367da90770f63b8')
    proof = data.read_checked(data.BASE/'PG12412-batch-runtime-post-v1/manifest.json',
        '490c60f253fb284855962bd4832a7ad3dc1cbedb6f3b52457f9fdd4d5fd9d6d0')
    plan = data.read_checked(data.BASE/'PG12405-batch-runtime-literal-source-post-v2/manifest.json',
        '3ff685e47422a09a15eb51f067e675b715a8854d6d14406e5d9e327326ea435d')
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json',
        'f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    old = [subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,old


def expected(prior,proof,plan):
    value=copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):value.pop(key,None)
    changed={r['path']:r for r in plan['sourceChanges']};bindings=[]
    for row in value['sourceRows']:
        if row['path'] not in changed:continue
        item=changed[row['path']];assert row['sha256']==item['beforeSha256'] and row['canonicalOwner']==row['canonicalCostOwner']==row['owner'];row['sha256']=item['sha256'];bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings)==1 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-F02'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    from trace_owner_join import join_rows,validate as validate_join
    logical={r['path']:r for r in json.loads((data.ROOT/INV).read_bytes())['artifacts']}
    owner_rows=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_rows,logical,hashes,'WBS-F02')
    validate_join(joined,owner_rows,logical,hashes,'WBS-F02')
    assert sum(r['ownershipStatus']=='UNKNOWN' for r in joined)==1
    # Original logical941 does not contain these Test paths. Keep the already approved registry
    # owner pairs, never infer acceptance from the current change group.
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentBatchRuntimeOracleBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=5,literalReferences=33,sameValueConstantIds=plan['sameValueConstantIds'],independentInverseNegativeVectors=15,originalOracleInverseNegativeVectors=6,oracleIntermediateSource=plan['oracleIntermediateSource'],approvedNewTestId='PT-BAT-283C',allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_CANONICAL_OWNER_PAIRS_NOT_INFERRED_FROM_CHANGE_OWNER',logicalJoinDoesNotReassignUnknown=True),
        currentBatchRuntimeOracleRuntimeQualification=dict(source=SOURCE,proofManifestSha256='490c60f253fb284855962bd4832a7ad3dc1cbedb6f3b52457f9fdd4d5fd9d6d0',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=3,uniqueMethods=3,originalMethods=2,newProductTestIds=1,suites=1,failures=0,errors=0,skipped=0,aborted=0,completeBatchMainClasses=645,productMainExecuted=False,mainCoverageQualification='NOT_APPLICABLE_NO_PRODUCT_MAIN_EXECUTED',measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=0,selectedValueFourCounters100=False,zeroDenominatorCountersAreNA=True,rawStatic=0,sourceLocalContexts=0,unclassifiedRaw=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousBatchRuntimeOracleRegistryReference' not in section
        section['previousBatchRuntimeOracleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2332_Batch標準SDK依存Oracle是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentBatchRuntimeOracleBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentBatchRuntimeOracleBinding',
            qualification='SOURCE_BOUND_ORIGINAL2_NEW_BAT283C_FIVE_LITERAL_FIXES_RAW0_POM_ONLY_NO_MAIN_EXECUTION_NOT_FORMAL')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,plan,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=observed,**expected(prior,proof,plan)))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap,_,_ = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,before,result in ((INV,raw,after),(SNAP,snap,asnap)):
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'
        lines = list(difflib.unified_diff(before.decode().splitlines(),result.decode().splitlines(),n=0))[2:]
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in lines)+'\n'
    return patch+'*** End Patch\n'


def contract(value,reference):
    if any(value.get(k) != v for k,v in reference.items()):
        raise ValueError('exact source/owner/cost/runtime metadata required')


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    # No applicability review claim: the measured8 warnings retain explicit source contexts and current whole pending.
    prior,proof,plan,(raw,snap) = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,plan)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (data.ROOT/INV).read_bytes() == after and (data.ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    bads = []
    for field,v in [('canonicalOwner','WBS-G13.07'),('canonicalCostOwner','WBS-F02'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference)
        bad['currentBatchRuntimeOracleBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',2),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentBatchRuntimeOracleRuntimeQualification'][field] = v
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,reference)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/owner/cost/runtime metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=1,
        allOtherPriorRowsUnchanged=982,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
