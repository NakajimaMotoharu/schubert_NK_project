"""Two API JDBC collector Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = '21daf2722f9b280ec005b1b971300774a1d3716f'
BASE = 'f7f48733a'
OUT = data.BASE/'PG11772-jdbc-collector-literal-trace-v1'
POST = data.BASE/'PG11774-jdbc-collector-literal-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11742-mq-recorder-literal-trace-v1/manifest.json',
        'c5a82030c8d64d3f0fb273f86fde3b03ac0da92fbb8643f728a47b10769b9801')
    proof = data.read_checked(data.BASE/'PG11770-jdbc-collector-literal-post-v1/manifest.json',
        'bc29e89b6700df09f1f7e76bc8939fd556dfe7187cddc8cedc4274ab15eb1411')
    plan = data.read_checked(data.BASE/'PG11760-jdbc-collector-literal-plan-v1/manifest.json',
        '18595a88e2013ad1724526cc3947fdc027958da2737ad23f83189549e53cb954')
    normal = data.read_checked(data.BASE/'PG11764-jdbc-collector-literal-six-compile-v1/manifest.json',
        'a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11771-jdbc-collector-owner-context-v1/manifest.json','64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1')
    context_post=data.read_checked(data.BASE/'PG11773-jdbc-collector-owner-context-post-v1/manifest.json','e2dba97dfdd1195e72f2abd48bacf56887e6820766711c9bdfa98159269f8cb1')
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
        currentJdbcCollectorLiteralBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=13,literalReferences=98,extractedPrefixAssignments=1,constants={r['path']:r['constants'] for r in plan['sourceChanges']},assignmentByPath={r['path']:r['assignmentExtracted'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=34,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentJdbcCollectorLiteralRuntimeQualification=dict(source=SOURCE,proofManifestSha256='bc29e89b6700df09f1f7e76bc8939fd556dfe7187cddc8cedc4274ab15eb1411',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=16,uniqueMethods=16,newProductTestIds=0,
            suites=2,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=None,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=2,selectedValueFourCounters100=True,rawStatic=12,sourceLocalContexts=12,existingReferencesReauthenticated=12,newSourceReasons=0,unclassifiedRaw=0,
            contextManifestSha256='64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1',contextPostManifestSha256='e2dba97dfdd1195e72f2abd48bacf56887e6820766711c9bdfa98159269f8cb1',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousJdbcCollectorLiteralRegistryReference' not in section
        section['previousJdbcCollectorLiteralRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2256_JdbcCollector同値十四是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentJdbcCollectorLiteralBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentJdbcCollectorLiteralBinding',
            qualification='SOURCE_BOUND_13_STRINGS_1_PREFIX_INCREMENT_ORIGINAL16_TWO_MAIN_FOUR100_RAW12_REAUTH_CURRENT_WHOLE_PENDING_FULL_API_NOT100')
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
        bad['currentJdbcCollectorLiteralBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentJdbcCollectorLiteralRuntimeQualification'][field] = v
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



