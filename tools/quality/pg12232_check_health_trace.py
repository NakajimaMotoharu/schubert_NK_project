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

SOURCE = 'd8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
BASE = 'ec2335685'
OUT = data.BASE/'PG12232-check-health-trace-v1'
POST = data.BASE/'PG12234-check-health-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12202-audit-metric-trace-v1/manifest.json',
        'b0a68a0a64aaf11d2b0abdd94814207edd67e9391e36f49354e254979e2d55be')
    proof = data.read_checked(data.BASE/'PG12230-check-health-post-v1/manifest.json',
        '318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa')
    plan = data.read_checked(data.BASE/'PG12220-check-health-plan-v1/manifest.json',
        '878a909ed94f2efd0fa8abe7178f4784d4dbb0a1ac6f1655c811b3952fdfae38')
    normal = data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json',
        'd65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12231-check-health-context-v1/manifest.json','2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86')
    context_post=data.read_checked(data.BASE/'PG12233-check-health-context-post-v1/manifest.json','bd3fe22d3fb448259d10d4b7afad63b976c1692816258e93e5131b49c60e7cdf')
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
    assert len(bindings)==2 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P009-03','WBS-P018-06'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentCheckHealthFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=10,literalReferences=76,readIncrementDecomposed=True,rawDiagnosticsCorrected=11,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=31,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentCheckHealthFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=8,uniqueMethods=8,newProductTestIds=0,suites=2,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,completeApiMainClasses=467,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=3,selectedValueFourCounters100=False,selectedApplicableCountersAllCovered=False,zeroDenominatorCountersAreNA=True,selectedValueMeasured=dict(LINE=72,METHOD=10,CLASS=3,BRANCH=56),selectedValueMissed=dict(LINE=1,METHOD=1,CLASS=0,BRANCH=4),rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,contextManifestSha256='2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86',contextPostManifestSha256='bd3fe22d3fb448259d10d4b7afad63b976c1692816258e93e5131b49c60e7cdf',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousCheckHealthFixtureRegistryReference' not in section
        section['previousCheckHealthFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2310_Checksum純Health十一是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentCheckHealthFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentCheckHealthFixtureBinding',
            qualification='SOURCE_BOUND_11_FIXES_INVERSE31_ORIGINAL8_CHECKSUM2_66L9M2C36B_MISS0_HEALTH_MISS1L1M4B_RAW2_CONTEXT2_FULL_API_WEB_NOT100_HOST_ONLY')
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
        bad['currentCheckHealthFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',28),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentCheckHealthFixtureRuntimeQualification'][field] = v
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
