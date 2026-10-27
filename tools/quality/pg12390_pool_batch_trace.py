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

SOURCE = '14198cb1878ec73319511ba1067133992d335e63'
BASE = '14198cb1878ec73319511ba1067133992d335e63'
OUT = data.BASE/'PG12390-pool-batch-trace-v1'
POST = data.BASE/'PG12392-pool-batch-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12360-pool-capacity-trace-v1/manifest.json',
        '9a5e109ab907bb8a5019881127c7924dbc93246b9bcd0b959ef601fab95321f7')
    proof = data.read_checked(data.BASE/'PG12384-pool-batch-post-v1/manifest.json',
        'c89e090a9e054d00206a094b29c0e41694cd87e3433f81211e1ae0048791724d')
    plan = data.read_checked(data.BASE/'PG12374-pool-batch-plan-v1/manifest.json',
        'e73107802e5b4d7605add4d2255393c02df82bd4d202306c4300e9ba5967e557')
    normal = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json',
        '27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12386-pool-batch-context-v1/manifest.json','f7c2f9ed8356a354b4c93755f783cff32d23c532a62129b7f1fcecf555e86a07')
    context_post=data.read_checked(data.BASE/'PG12388-pool-batch-context-post-v1/manifest.json','4add8469630e4c0325a7db3698013a3d0f1af78804526ae688e278d6185b8152')
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
    assert len(bindings)==5 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P018-09'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    from trace_owner_join import join_rows,validate as validate_join
    logical={r['path']:r for r in json.loads((data.ROOT/INV).read_bytes())['artifacts']}
    owner_rows=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_rows,logical,hashes,'WBS-F03')
    validate_join(joined,owner_rows,logical,hashes,'WBS-F03')
    assert sum(r['ownershipStatus']=='UNKNOWN' for r in joined)==0
    assert next(r for r in joined if r['ownershipStatus']!='UNKNOWN')['canonicalOwner']=='WBS-P018-09'
    # Original logical941 does not contain these Test paths. Keep the already approved registry
    # owner pairs, never infer acceptance from the current change group.
    value.update(source=SOURCE,oldRowsChangedShaOnly=5,allOtherPriorRowsUnchanged=978,
        currentPoolBatchFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=9,literalReferences=73,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=42,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_CANONICAL_OWNER_PAIRS_NOT_INFERRED_FROM_CHANGE_OWNER',logicalJoinDoesNotReassignUnknown=True),
        currentPoolBatchFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='c89e090a9e054d00206a094b29c0e41694cd87e3433f81211e1ae0048791724d',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=38,uniqueMethods=38,newProductTestIds=0,suites=5,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=358,completeBatchMainClasses=645,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=19,selectedValueFourCounters100=False,zeroDenominatorCountersAreNA=True,rawStatic=26,sourceLocalContexts=26,unclassifiedRaw=0,contextManifestSha256='f7c2f9ed8356a354b4c93755f783cff32d23c532a62129b7f1fcecf555e86a07',contextPostManifestSha256='4add8469630e4c0325a7db3698013a3d0f1af78804526ae688e278d6185b8152',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousPoolBatchFixtureRegistryReference' not in section
        section['previousPoolBatchFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2329_供給PoolCollector・Batch監視九件_製造単体結果.md',currentAddedTestPaths=[])
        section['currentPoolBatchFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentPoolBatchFixtureBinding',
            qualification='SOURCE_BOUND_9_FIXES_INVERSE42_ORIGINAL38_RAW26_CONTEXT26_FULL_API_WEB_BATCH_NOT100_HOST_ONLY')
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
        bad['currentPoolBatchFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',37),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentPoolBatchFixtureRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=5,
        allOtherPriorRowsUnchanged=978,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
