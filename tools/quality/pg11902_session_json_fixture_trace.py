"""One session JSON fixture Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = '264dc69591876147d76c19082cb69658cfe03dd8'
BASE = '62d8d64f7'
OUT = data.BASE/'PG11902-session-json-fixture-trace-v1'
POST = data.BASE/'PG11904-session-json-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11872-web-exporter-fixture-trace-v1/manifest.json',
        '5991784004057fddac7cfe1825f611c2d63520fe1f433427219d183a266d7148')
    proof = data.read_checked(data.BASE/'PG11900-session-json-fixture-post-v1/manifest.json',
        '66153a5517f24a764afb9405ea3ad93b31cc1e8f99bd0f276535d723c40ff9d0')
    plan = data.read_checked(data.BASE/'PG11890-session-json-fixture-plan-v1/manifest.json',
        'a74a3356b751e8464e72b7e7f799cfb3c40ba87dd7806fbd7e8cef4c96d727b6')
    normal = data.read_checked(data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json',
        '3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG11901-session-json-owner-context-v1/manifest.json','bed3fc58d5eb27a5c30ca955caa7617f50bf36d3710b5fad401f76f7c92140da')
    context_post=data.read_checked(data.BASE/'PG11903-session-json-owner-context-post-v1/manifest.json','4073735d7018916a738d9bae1b7409f011c27ba9f2e551c21638978dad5d3999')
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
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P015-01'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentSessionJsonFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=6,literalReferences=33,orderConstants=1,comparisonReferences=1,constants={r['path']:r['constants'] for r in plan['sourceChanges']},
            independentInverseNegativeVectors=20,rawJavaTokensRestored=3666,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentSessionJsonFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='66153a5517f24a764afb9405ea3ad93b31cc1e8f99bd0f276535d723c40ff9d0',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=12,uniqueMethods=12,changedFixtureMethods=7,relatedUnchangedV2Methods=5,newProductTestIds=0,
            suites=2,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=None,completeWebMainClasses=358,
            measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,
            selectedValueMainClasses=1,selectedValueFourCounters100=True,rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,
            contextManifestSha256='bed3fc58d5eb27a5c30ca955caa7617f50bf36d3710b5fad401f76f7c92140da',contextPostManifestSha256='4073735d7018916a738d9bae1b7409f011c27ba9f2e551c21638978dad5d3999',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousSessionJsonFixtureRegistryReference' not in section
        section['previousSessionJsonFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2272_SessionJSON七命名_製造単体結果.md',currentAddedTestPaths=[])
        section['currentSessionJsonFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentSessionJsonFixtureBinding',
            qualification='SOURCE_BOUND_6_STRINGS_33_REFS_INDEX1_STRICT3666_ORIGINAL7_PLUS_V2_FIVE_CODEC_FOUR100_RAW2_CURRENT_CONTEXT_FULL_WEB_NOT100')
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
        bad['currentSessionJsonFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentSessionJsonFixtureRuntimeQualification'][field] = v
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



