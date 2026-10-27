"""One storage attribute fixture Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = 'fd113e37b0783ae86d50696c9d3844e80b258d8a'
BASE = '552720aca'
OUT = data.BASE/'PG11932-storage-attribute-fixture-trace-v1'
POST = data.BASE/'PG11934-storage-attribute-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11902-session-json-fixture-trace-v1/manifest.json',
        '00e6893f9199cadc22404ad98cffcc76a339230838318ed86140a66deaa4505a')
    proof = data.read_checked(data.BASE/'PG11930-storage-attribute-fixture-post-v1/manifest.json',
        '1bf9eba710e500037a4dd7e1eb008151cc1c389d24726ba2481765fca200b86b')
    plan = data.read_checked(data.BASE/'PG11920-storage-attribute-fixture-plan-v1/manifest.json',
        '510afeb4ee42cfa6dac9c4a737a7e1766932fb62e9b3d84d855fc03d2163301e')
    normal = data.read_checked(data.BASE/'PG11924-storage-attribute-fixture-six-compile-v1/manifest.json',
        '6c9f579aa08c720ce523423efa8ca7dc64a941dac559a548927259f09f28555c')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11931-storage-attribute-map-context-v1/manifest.json','953bad12f2072ba6ae09f3462526b080dd06c6064dda06df73e3670ae17a462b')
    context_post=data.read_checked(data.BASE/'PG11933-storage-attribute-map-context-post-v1/manifest.json','1b1656e75eafa77239ce41445e0ef7883d2901c8dcc7a37dca064a4d59c0ce26')
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
    assert len(bindings) == 1 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P003-05'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentStorageAttributeFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=5,literalReferences=55,modeLiteralPoints=27,boundConstants=1,comparisonReferences=1,constants={r['path']:r['constants'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=45,integerMetadataNegativeVectors=27,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentStorageAttributeFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='1bf9eba710e500037a4dd7e1eb008151cc1c389d24726ba2481765fca200b86b',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=7,uniqueMethods=7,changedFixtureMethods=7,newProductTestIds=0,
            suites=1,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=None,completeWebMainClasses=None,completeStorageMainClasses=80,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=1,selectedValueFourCounters100=True,rawStatic=1,sourceLocalContexts=1,unclassifiedRaw=0,
            contextManifestSha256='953bad12f2072ba6ae09f3462526b080dd06c6064dda06df73e3670ae17a462b',contextPostManifestSha256='1b1656e75eafa77239ce41445e0ef7883d2901c8dcc7a37dca064a4d59c0ce26',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousStorageAttributeFixtureRegistryReference' not in section
        section['previousStorageAttributeFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2276_Storage属性三十三是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentStorageAttributeFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentStorageAttributeFixtureBinding',
            qualification='SOURCE_BOUND_27_MODE_VALUES_5_STRINGS_55_REFS_BOUND1_ORIGINAL7_GUARD_MEASURED_FOUR100_PRIVATE_CTOR_FILTERED_RAW1_REQUIRED_NULL_FIXTURE_FULL_STORAGE_NOT100')
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
        bad['currentStorageAttributeFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentStorageAttributeFixtureRuntimeQualification'][field] = v
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



