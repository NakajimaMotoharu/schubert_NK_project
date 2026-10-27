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

SOURCE = '4b5f6faa078be348132a6ece9140b0c1a31d7907'
BASE = '18aa3d682'
OUT = data.BASE/'PG12202-audit-metric-trace-v1'
POST = data.BASE/'PG12204-audit-metric-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12172-audit-fixture-trace-v1/manifest.json',
        '9f8f91ef46a6aec9729c6915aa4ac3ef1339ffbf81789ec5c911638e03c846c4')
    proof = data.read_checked(data.BASE/'PG12200-audit-metric-post-v1/manifest.json',
        '554698fe99408bc21057694826c982c3ab4d6eafe44629ae4cf9cdaf1c9e20fb')
    plan = data.read_checked(data.BASE/'PG12190-audit-metric-plan-v1/manifest.json',
        'ca016a660ab8d1b8cff676b69b3d4be922e9494a41f87ea9855c749c85870c43')
    normal = data.read_checked(data.BASE/'PG12194-audit-metric-six-compile-v1/manifest.json',
        '971ee001e169f9fa05df627e0cd0789704518d952105c27328eabf86ebd4adff')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12201-audit-metric-context-v1/manifest.json','12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2')
    context_post=data.read_checked(data.BASE/'PG12203-audit-metric-context-post-v1/manifest.json','f7b5d181661634f8cfff2aade0bbf30eefc7d22ae0942cfac58d529b64ca9e07')
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
    assert len(bindings)==3 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P006-04','WBS-P018-09'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=3,allOtherPriorRowsUnchanged=980,
        currentAuditMetricFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=5,literalReferences=40,fieldRenames=3,ifIndexConstants=1,rawDiagnosticsCorrected=9,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=24,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentAuditMetricFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='554698fe99408bc21057694826c982c3ab4d6eafe44629ae4cf9cdaf1c9e20fb',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=19,uniqueMethods=19,newProductTestIds=0,suites=3,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,completeBatchMainClasses=645,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=7,selectedValueFourCounters100=True,selectedApplicableCountersAllCovered=True,zeroDenominatorCountersAreNA=True,selectedValueMeasured=dict(LINE=172,METHOD=28,CLASS=7,BRANCH=84),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=5,sourceLocalContexts=5,unclassifiedRaw=0,contextManifestSha256='12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2',contextPostManifestSha256='f7b5d181661634f8cfff2aade0bbf30eefc7d22ae0942cfac58d529b64ca9e07',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousAuditMetricFixtureRegistryReference' not in section
        section['previousAuditMetricFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2307_監査Metric九是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentAuditMetricFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentAuditMetricFixtureBinding',
            qualification='SOURCE_BOUND_9_RAW_FIXES_STRICT_INVERSE24_ORIGINAL19_AUDIT3_METRIC4_172L28M7C84B_MISS0_RAW5_CONTEXT5_FULL_BATCH_WEB_NOT100_HOST_ONLY')
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
        bad['currentAuditMetricFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentAuditMetricFixtureRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=3,
        allOtherPriorRowsUnchanged=980,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
