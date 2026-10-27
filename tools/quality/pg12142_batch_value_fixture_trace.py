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

SOURCE = '8a229695c0ea503ebac8761993665242eeba0107'
BASE = '8aec63dcd'
OUT = data.BASE/'PG12142-batch-value-fixture-trace-v1'
POST = data.BASE/'PG12144-batch-value-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12112-authz-fixture-trace-v1/manifest.json',
        '951a1f1c17f35efe7b51e0a4fa55451959726f3ead61201c1687d924d369f015')
    proof = data.read_checked(data.BASE/'PG12145-batch-value-fixture-post-v2/manifest.json',
        '3ce8bd128c33539f9ef8eb6b953d37e550e54c64be6a7b98d914e460d6633de2')
    plan = data.read_checked(data.BASE/'PG12130-batch-value-fixture-plan-v1/manifest.json',
        'e605ba4aa54692bb840093735ea245f6088f93bd9d702213dbe407101820098b')
    normal = data.read_checked(data.BASE/'PG12134-batch-value-fixture-six-compile-v1/manifest.json',
        '6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12141-batch-value-fixture-context-v1/manifest.json','f7de8c789c6e84d9663b892c5646561e981b3cdda626321565f45b994f684da6')
    context_post=data.read_checked(data.BASE/'PG12143-batch-value-fixture-context-post-v1/manifest.json','b1ba08a8aff7c90d790484d1331ab06dccabbf9ab75828e953825b51d5c701e5')
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
    assert len(bindings)==2 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P018-04','WBS-P017-10'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentBatchValueFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=12,literalReferences=59,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=30,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentBatchValueFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='3ce8bd128c33539f9ef8eb6b953d37e550e54c64be6a7b98d914e460d6633de2',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=4,uniqueMethods=4,newProductTestIds=0,suites=2,failures=0,errors=0,skipped=0,aborted=0,completeBatchMainClasses=645,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=5,selectedValueFourCounters100=True,selectedApplicableCountersAllCovered=True,zeroDenominatorCountersAreNA=True,selectedValueMeasured=dict(LINE=64,METHOD=20,CLASS=5,BRANCH=4),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=1,sourceLocalContexts=1,unclassifiedRaw=0,contextManifestSha256='f7de8c789c6e84d9663b892c5646561e981b3cdda626321565f45b994f684da6',contextPostManifestSha256='b1ba08a8aff7c90d790484d1331ab06dccabbf9ab75828e953825b51d5c701e5',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousBatchValueFixtureRegistryReference' not in section
        section['previousBatchValueFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2300_Batch純値十二是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentBatchValueFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentBatchValueFixtureBinding',
            qualification='SOURCE_BOUND_12_STRINGS_59_REFS_ORIGINAL4_ENUM5_64L20M5C4B_MISS0_RAW1_LOADER_CONTEXT_FULL_BATCH_NOT100_OUTER178_METHOD_INSTRUCTION0_HOST_ONLY')
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
        bad['currentBatchValueFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentBatchValueFixtureRuntimeQualification'][field] = v
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
