"""Two supplied MQ/media collector Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = '69d50093df9e655a39eadcd7a392646ff65bfbb0'
BASE = '96d58a322'
OUT = data.BASE/'PG11842-mq-media-collector-value-trace-v1'
POST = data.BASE/'PG11844-mq-media-collector-value-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11812-job-outbox-value-literal-trace-v1/manifest.json',
        '85472122436148adf180f0e0f7e09667d35b3ff211bdb9de003eb517256c70c6')
    proof = data.read_checked(data.BASE/'PG11840-mq-media-collector-value-post-v1/manifest.json',
        'a7e0e82cb52c1a3c4d40d0aaf9a071d6c539455b869f2fe0aebfa8df66f5de7c')
    plan = data.read_checked(data.BASE/'PG11830-mq-media-collector-value-plan-v1/manifest.json',
        '91285e0291b3636247a2e37209dbd6cd44064c6bec1cd82bd9aa448e428ad0ea')
    normal = data.read_checked(data.BASE/'PG11834-mq-media-collector-value-six-compile-v1/manifest.json',
        '878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11841-mq-media-collector-owner-context-v1/manifest.json','a86573a6cd91408d192bf148f327295e306f5a07821518ac2b2fcccb759fa54e')
    context_post=data.read_checked(data.BASE/'PG11843-mq-media-collector-owner-context-post-v1/manifest.json','0179fd915f8964f4b36fcdb5d91db9423be8a51f6d9af2cd3502aa775ba05e44')
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
    assert len(bindings) == 2 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentMqMediaCollectorValueBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=9,literalReferences=67,orderConstants=2,comparisonReferences=2,constants={r['path']:r['constants'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=34,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentMqMediaCollectorValueRuntimeQualification=dict(source=SOURCE,proofManifestSha256='a7e0e82cb52c1a3c4d40d0aaf9a071d6c539455b869f2fe0aebfa8df66f5de7c',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=16,uniqueMethods=16,newProductTestIds=0,
            suites=2,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=358,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=2,selectedValueFourCounters100=True,rawStatic=20,sourceLocalContexts=20,unclassifiedRaw=0,
            contextManifestSha256='a86573a6cd91408d192bf148f327295e306f5a07821518ac2b2fcccb759fa54e',contextPostManifestSha256='0179fd915f8964f4b36fcdb5d91db9423be8a51f6d9af2cd3502aa775ba05e44',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousMqMediaCollectorValueRegistryReference' not in section
        section['previousMqMediaCollectorValueRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2264_MqMedia供給collector十一命名_製造単体結果.md',currentAddedTestPaths=[])
        section['currentMqMediaCollectorValueBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentMqMediaCollectorValueBinding',
            qualification='SOURCE_BOUND_9_STRINGS_67_REFS_2_READ_ORDINALS_ORIGINAL16_TWO_COLLECTOR_FOUR100_RAW20_CURRENT_CONTEXT_FULL_ARTIFACTS_NOT100')
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
        bad['currentMqMediaCollectorValueBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentMqMediaCollectorValueRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=2,
        allOtherPriorRowsUnchanged=981,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()



