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

SOURCE = '7368ba9d4a38677f5eade903771832e612aa42b5'
BASE = '7368ba9d4a38677f5eade903771832e612aa42b5'
OUT = data.BASE/'PG12294-api-value-trace-v1'
POST = data.BASE/'PG12296-api-value-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12232-check-health-trace-v1/manifest.json',
        '090aeb1ffbd30cc6ff65a03d9b437580cd30ece93292cde31e765471e863221b')
    proof = data.read_checked(data.BASE/'PG12292-api-value-post-v1/manifest.json',
        '443e7cf38169f2a1197358b23a62d870e37d39037a49ea53a277a064e4c0b894')
    plan = data.read_checked(data.BASE/'PG12285-api-value-plan-v3/manifest.json',
        '350e7513bbd53a67ff76ec960a6e4a17e9360c129a1d5c2149f56a968ff43823')
    normal = data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json',
        '776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12293-api-value-context-v1/manifest.json','4d3f6cf82d1bb4d5a0a5a3a50afcfe3accea90fa446dd9fe634daf1e6f87abb1')
    context_post=data.read_checked(data.BASE/'PG12295-api-value-context-post-v1/manifest.json','94f068630be89a535e7666b02f140bd3692442a4a06f360bcb4367733fe88e38')
    assert context['source']==context_post['source']==SOURCE and context['actualExit']==context_post['actualExit']==0
    old = [subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,old


def expected(prior,proof,plan):
    value=copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):value.pop(key,None)
    changed={r['path']:r for r in plan['sourceChanges']};bindings=[]
    for row in value['sourceRows']:
        if row['path'] not in changed:continue
        item=changed[row['path']];assert row['sha256']==item['beforeSha256'] and row['canonicalOwner']==row['canonicalCostOwner']==row['owner'];row['sha256']=item['sha256'];bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings)==4 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P012-02','WBS-P007-01','WBS-P006-02','WBS-P018-09'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    from trace_owner_join import join_rows,validate as validate_join
    logical={r['path']:r for r in json.loads((data.ROOT/INV).read_bytes())['artifacts']}
    owner_rows=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_rows,logical,hashes,'WBS-F03')
    validate_join(joined,owner_rows,logical,hashes,'WBS-F03')
    assert sum(r['ownershipStatus']=='UNKNOWN' for r in joined)==3
    assert next(r for r in joined if r['ownershipStatus']!='UNKNOWN')['canonicalOwner']=='WBS-P018-09'
    # Original logical941 does not contain these Test paths. Keep the already approved registry
    # owner pairs, never infer the three UNKNOWN join outcomes from the current change group.
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentApiValueFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=9,literalReferences=50,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=30,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_CANONICAL_OWNER_PAIRS_NOT_INFERRED_FROM_CHANGE_OWNER',logicalJoinDoesNotReassignUnknown=True),
        currentApiValueFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='443e7cf38169f2a1197358b23a62d870e37d39037a49ea53a277a064e4c0b894',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=18,uniqueMethods=18,newProductTestIds=0,suites=4,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=13,selectedValueFourCounters100=False,zeroDenominatorCountersAreNA=True,rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,contextManifestSha256='4d3f6cf82d1bb4d5a0a5a3a50afcfe3accea90fa446dd9fe634daf1e6f87abb1',contextPostManifestSha256='94f068630be89a535e7666b02f140bd3692442a4a06f360bcb4367733fe88e38',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousApiValueFixtureRegistryReference' not in section
        section['previousApiValueFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2318_API純値四fixture九件_製造単体結果.md',currentAddedTestPaths=[])
        section['currentApiValueFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentApiValueFixtureBinding',
            qualification='SOURCE_BOUND_9_FIXES_INVERSE30_ORIGINAL18_RAW2_CONTEXT2_FULL_API_NOT100_HOST_ONLY')
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
    for field,v in [('canonicalOwner','WBS-G13.07'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference)
        bad['currentApiValueFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentApiValueFixtureRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=4,
        allOtherPriorRowsUnchanged=979,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
