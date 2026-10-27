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

SOURCE = 'ee82637a750105243ddeac665c61d27a781e5cf1'
BASE = 'ef64924eb'
OUT = data.BASE/'PG12112-authz-fixture-trace-v1'
POST = data.BASE/'PG12114-authz-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12082-media-wire-fixture-trace-v1/manifest.json',
        'd7b6a369b579683c9f0d942978940e375a07703154473aefd346292f3a1132fe')
    proof = data.read_checked(data.BASE/'PG12110-authz-fixture-post-v1/manifest.json',
        '633bd25ec34b7ba5bd4549445856dd8653fbae1c4e6c16d30125b87441515760')
    plan = data.read_checked(data.BASE/'PG12100-authz-fixture-plan-v1/manifest.json',
        'df6edfac15c8e9a7a0fc31cc1af15ded727ab90db9c7de0c0cd993e09ecfd49c')
    normal = data.read_checked(data.BASE/'PG12104-authz-fixture-six-compile-v1/manifest.json',
        '1cffddad23dd78451013a1bb325a7e84682d733fb80d57f3205279d12d9774f9')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12111-authz-fixture-context-v1/manifest.json','6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22')
    context_post=data.read_checked(data.BASE/'PG12113-authz-fixture-context-post-v1/manifest.json','59fa4f28c7d477a4b920f17edb772d16447dc3145220aa36cb2ffc60dd334158')
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
    assert len(bindings)==1 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P015-02'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentAuthorizationFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=10,literalReferences=63,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=24,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentAuthorizationFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='633bd25ec34b7ba5bd4549445856dd8653fbae1c4e6c16d30125b87441515760',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=4,uniqueMethods=4,newProductTestIds=0,suites=1,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=1,selectedValueFourCounters100=False,selectedApplicableCountersAllCovered=True,branchZeroDenominatorIsNA=True,selectedValueMeasured=dict(LINE=21,METHOD=3,CLASS=1,BRANCH=0),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=3,sourceLocalContexts=3,unclassifiedRaw=0,contextManifestSha256='6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22',contextPostManifestSha256='59fa4f28c7d477a4b920f17edb772d16447dc3145220aa36cb2ffc60dd334158',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousAuthorizationFixtureRegistryReference' not in section
        section['previousAuthorizationFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2297_Mock権限表十是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentAuthorizationFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentAuthorizationFixtureBinding',
            qualification='SOURCE_BOUND_10_STRINGS_63_REFS_ORIGINAL4_CLEAR_HOOK_FACTORY21L3M1C_MISS0_BRANCH0_NA_RAW3_REQUIRED_CONTEXT_FULL_WEB_NOT100')
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
        bad['currentAuthorizationFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentAuthorizationFixtureRuntimeQualification'][field] = v
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
