"""Three API supplied job/outbox value Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = '60f62bd5dffb11e9943fc7578d9bddf380f8003c'
BASE = 'bc0c26faa'
OUT = data.BASE/'PG11812-job-outbox-value-literal-trace-v1'
POST = data.BASE/'PG11814-job-outbox-value-literal-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11772-jdbc-collector-literal-trace-v1/manifest.json',
        '3a81588ff2bc82ed6d67b49a97856a08de85c5d291aed089db4e5238f4d36514')
    proof = data.read_checked(data.BASE/'PG11810-job-outbox-value-literal-post-v1/manifest.json',
        'c5378e66859ab942a09b9bad4dc74dea3cd7568b06a369db6306626f19130298')
    plan = data.read_checked(data.BASE/'PG11800-job-outbox-value-literal-plan-v1/manifest.json',
        'bde68c853c70a3c82b9b35186b84e99019af09fd1549919dbc6ddd6db76abe1e')
    normal = data.read_checked(data.BASE/'PG11804-job-outbox-value-literal-six-compile-v1/manifest.json',
        'cfa574ea833d73ee31adfb96fba25fb5909890a2fb1fe32413049618b4ca58ea')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11811-job-outbox-value-owner-context-v1/manifest.json','cafc772777dea065b2c37ceeb582cda3418475ea2efed811bd28f21fcdca1eac')
    context_post=data.read_checked(data.BASE/'PG11813-job-outbox-value-owner-context-post-v1/manifest.json','d729d2e4d2a8834d864b2f9efe8ab26e5cd9f95edae97e72dae505972f07056c')
    assert context['source']==context_post['source']==SOURCE and context['actualExit']==context_post['actualExit']==0
    old = [subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,old


def expected(prior,proof,plan):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    changed = {r['path']:r for r in plan['sourceChanges']}
    bindings = []
    for row in value['sourceRows']:
        if row['path'] not in changed:
            continue
        item = changed[row['path']]
        assert row['sha256'] == item['beforeSha256'] and row['canonicalOwner'] == row['canonicalCostOwner'] == row['owner']
        row['sha256'] = item['sha256']
        bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings) == 3 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=3,allOtherPriorRowsUnchanged=980,
        currentJobOutboxValueLiteralBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=10,literalReferences=73,orderConstants=3,comparisonReferences=3,constants={r['path']:r['constants'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=41,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentJobOutboxValueLiteralRuntimeQualification=dict(source=SOURCE,proofManifestSha256='c5378e66859ab942a09b9bad4dc74dea3cd7568b06a369db6306626f19130298',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=28,uniqueMethods=28,changedRecorderMethods=24,selectedUnchangedGeneratedMethods=4,unselectedUnchangedGeneratedMethodsNotPassed=[1,2,6,7],newProductTestIds=0,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=None,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=8,selectedValueFourCounters100=True,rawStatic=12,sourceLocalContexts=12,existingReferencesReauthenticated=6,newSourceReasons=6,unclassifiedRaw=0,
            contextManifestSha256='cafc772777dea065b2c37ceeb582cda3418475ea2efed811bd28f21fcdca1eac',contextPostManifestSha256='d729d2e4d2a8834d864b2f9efe8ab26e5cd9f95edae97e72dae505972f07056c',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousJobOutboxValueLiteralRegistryReference' not in section
        section['previousJobOutboxValueLiteralRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2260_JobOutbox供給値十命名_製造単体結果.md',currentAddedTestPaths=[])
        section['currentJobOutboxValueLiteralBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentJobOutboxValueLiteralBinding',
            qualification='SOURCE_BOUND_10_STRINGS_3_FAULT_MARKERS_CURRENT28_SELECTED8_ALL_MISSED_ZERO_ENUM_BRANCH_NA_RAW12_CURRENT_CONTEXT_PENDING_FULL_API_NOT100')
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
    # No applicability review claim: the measured12 warnings retain explicit source contexts and current whole pending.
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
        bad['currentJobOutboxValueLiteralBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentJobOutboxValueLiteralRuntimeQualification'][field] = v
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



