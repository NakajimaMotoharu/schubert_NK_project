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

SOURCE = '92c80a593717465426a33bdf581bc7e94b1235f1'
BASE = 'a98d39e99'
OUT = data.BASE/'PG12172-audit-fixture-trace-v1'
POST = data.BASE/'PG12174-audit-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12142-batch-value-fixture-trace-v1/manifest.json',
        '95182aa0540dc507d795ad23a7ac7ade2226a1d8fc1cb7c43fc79c895db08abc')
    proof = data.read_checked(data.BASE/'PG12170-audit-fixture-post-v1/manifest.json',
        '6c89ad1065f665b2feb5cc056e5354be4bad0c3a7e0f3358e4869a0e116d42c7')
    plan = data.read_checked(data.BASE/'PG12160-audit-fixture-plan-v1/manifest.json',
        '6e3f48753d372925ee8fdb5e31f7a6c72442963500c5567bdeb3fd6b393ff84e')
    normal = data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json',
        '462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12175-audit-fixture-context-v2/manifest.json','6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e')
    context_post=data.read_checked(data.BASE/'PG12173-audit-fixture-context-post-v1/manifest.json','c099169331bb672f774c0833491c98dcb808eba0f8028ec68dd67970c70cefb6')
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
    assert len(bindings)==1 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P006-04'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentLocalAuditFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=13,literalReferences=66,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=29,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentLocalAuditFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='6c89ad1065f665b2feb5cc056e5354be4bad0c3a7e0f3358e4869a0e116d42c7',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=6,uniqueMethods=6,newProductTestIds=0,suites=1,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=3,selectedValueFourCounters100=True,selectedApplicableCountersAllCovered=True,zeroDenominatorCountersAreNA=True,selectedValueMeasured=dict(LINE=89,METHOD=11,CLASS=3,BRANCH=52),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=5,sourceLocalContexts=3,unclassifiedRaw=2,contextManifestSha256='6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e',contextPostManifestSha256='c099169331bb672f774c0833491c98dcb808eba0f8028ec68dd67970c70cefb6',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousLocalAuditFixtureRegistryReference' not in section
        section['previousLocalAuditFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2304_Web局所監査十三定数_製造単体結果.md',currentAddedTestPaths=[])
        section['currentLocalAuditFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentLocalAuditFixtureBinding',
            qualification='SOURCE_BOUND_13_STRINGS_66_REFS_ORIGINAL6_AUDIT3_89L11M3C52B_MISS0_RAW5_CONTEXT3_UNCLASSIFIED2_FULL_WEB_NOT100_HOST_ONLY')
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
        bad['currentLocalAuditFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentLocalAuditFixtureRuntimeQualification'][field] = v
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
