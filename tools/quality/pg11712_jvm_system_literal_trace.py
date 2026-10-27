"""Four API/Web JVM-system Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = 'eee3d32be87396f61f94e6013f4864330ceee4f3'
BASE = '410b2b26b'
OUT = data.BASE/'PG11712-jvm-system-literal-trace-v1'
POST = data.BASE/'PG11714-jvm-system-literal-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11682-standard-composition-literal-trace-v1/manifest.json',
        '13bf63d703563dadf0f6e53520e280439a73a286ff87e3a3ada300d82500b522')
    proof = data.read_checked(data.BASE/'PG11710-jvm-system-literal-post-v1/manifest.json',
        'f537d671e637a3d80d1ef1e437cad7cc41b6e2b8f972c6bc0cdfb0859b269bfc')
    plan = data.read_checked(data.BASE/'PG11700-jvm-system-literal-plan-v1/manifest.json',
        '918f9082cad60641a70506b143d3ac67da65401d48e9fbb922bddd331eb8ddf4')
    normal = data.read_checked(data.BASE/'PG11704-jvm-system-literal-six-compile-v1/manifest.json',
        'e4715f0201f26ed2372db61d1c97e23c0c2b80fb6d7ff309053a74fb93e36e83')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11711-jvm-system-owner-context-v1/manifest.json','87b6809f45d7227b9ed1bb8e8deb642a3885b88c57492b319d550c3d5f96efe9')
    context_post=data.read_checked(data.BASE/'PG11713-jvm-system-owner-context-post-v1/manifest.json','19506bb83ccf33ea04fa3c595dc2b8f5aeff4741c08984d09600233eef954eb4')
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
    assert len(bindings) == 4 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentJvmSystemLiteralBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=14,literalReferences=100,orderConstants=4,comparisonReferences=4,constants={r['path']:r['constants'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=56,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentJvmSystemLiteralRuntimeQualification=dict(source=SOURCE,proofManifestSha256='f537d671e637a3d80d1ef1e437cad7cc41b6e2b8f972c6bc0cdfb0859b269bfc',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=56,uniqueMethods=56,newProductTestIds=0,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=358,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=4,selectedValueFourCounters100=True,rawStatic=16,sourceLocalContexts=16,unclassifiedRaw=0,
            contextManifestSha256='87b6809f45d7227b9ed1bb8e8deb642a3885b88c57492b319d550c3d5f96efe9',contextPostManifestSha256='19506bb83ccf33ea04fa3c595dc2b8f5aeff4741c08984d09600233eef954eb4',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousJvmSystemLiteralRegistryReference' not in section
        section['previousJvmSystemLiteralRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2248_JvmSystem同値十八是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentJvmSystemLiteralBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentJvmSystemLiteralBinding',
            qualification='SOURCE_BOUND_14_STRINGS_4_ORDER_CONSTANTS_ORIGINAL56_FOUR_MAIN_FOUR100_RAW16_CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING_FULL_ARTIFACTS_NOT100')
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
    # No applicability review claim: the measured16 warnings retain explicit source contexts and current whole pending.
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
        bad['currentJvmSystemLiteralBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentJvmSystemLiteralRuntimeQualification'][field] = v
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



