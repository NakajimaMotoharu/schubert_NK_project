"""Web record four new contracts/source owner/cost and directly measured nine Main qualification."""
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

SOURCE = '54e84fe04836dd88c3adfda5ac3f010eb591a7ee'
BASE = '2c043b0d5'
OUT = data.BASE/'PG12024-web-business-record-trace-v1'
POST = data.BASE/'PG12026-web-business-record-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11992-web-business-wire-fixture-trace-v1/manifest.json',
        '66488e1c299fc1d6150a246d8f1fc0ead09c08d945f8d93c8833c060aeb8c370')
    proof = data.read_checked(data.BASE/'PG12022-web-business-record-post-v1/manifest.json',
        'c5d6237eca375bc4735b29fab91cc52ca8e57b3667d36836b0591eb73e709e17')
    plan = data.read_checked(data.BASE/'PG12012-web-business-record-oracle-plan-v1/manifest.json',
        'c550a50234d1798bc97b34a3cee5e3cc5f57b73eead048943d87985170181aba')
    normal = data.read_checked(data.BASE/'PG12016-web-business-record-six-compile-v1/manifest.json',
        '214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12023-web-business-record-owner-context-v1/manifest.json','4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13')
    context_post=data.read_checked(data.BASE/'PG12025-web-business-record-owner-context-post-v1/manifest.json','226c47f3145461e122cf49fc96a8295e9119212d56fd20719af9007f652f8d4c')
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
    assert len(bindings)==1 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P005-02'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentWebBusinessRecordBinding=dict(source=SOURCE,sourceChanges=bindings,originalMethodsPreserved=8,addedTestMethods=4,totalMethods=12,independentGoldenVectors=3,goldenPlanManifestSha256='c550a50234d1798bc97b34a3cee5e3cc5f57b73eead048943d87985170181aba',sourcePostManifestSha256='d08647673459a18664b757eab45a393a3588bb225d3d7935589aa9173f9a8a17',independentSourceNegativeVectors=12,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentWebBusinessRecordRuntimeQualification=dict(source=SOURCE,proofManifestSha256='c5d6237eca375bc4735b29fab91cc52ca8e57b3667d36836b0591eb73e709e17',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=12,uniqueMethods=12,newProductTestIds=4,suites=1,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=9,selectedValueFourCounters100=True,selectedValueMeasured=dict(LINE=113,METHOD=24,CLASS=9,BRANCH=26),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,contextManifestSha256='4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13',contextPostManifestSha256='226c47f3145461e122cf49fc96a8295e9119212d56fd20719af9007f652f8d4c',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousWebBusinessRecordRegistryReference' not in section
        section['previousWebBusinessRecordRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2288_Web共通wire_record境界追加PT結果.md',currentAddedTestPaths=[])
        section['currentWebBusinessRecordBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentWebBusinessRecordBinding',
            qualification='SOURCE_BOUND_ORIGINAL8_PLUS4_RECORD_UI_GOLDEN3_DIRECT9_113L24M9C26B_MISS0_BRANCH_ZERO_NA_RAW2_FINITE_THREAD_FULL_WEB_NOT100')
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
        bad['currentWebBusinessRecordBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentWebBusinessRecordRuntimeQualification'][field] = v
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
