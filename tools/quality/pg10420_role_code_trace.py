"""Three Test-only oracle source bindings, preserving all other rows and historical runtime."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate

ROOT = data.ROOT
BASE = '753b61c55'
SOURCE = 'b8234ad5a1403e944acaf8e13f1e5f07a22309bd'
PRIOR = '548178c53d57f1caeed9dab38d2ca643f38b645c8cc2fed3d8bfe9e5e2e7f33e'
PROOF = '4a50827d1a97a6f6fda1df03d484edd7eeee0e3f135bd9b76fcb8ff7861e67ae'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT,POST = data.BASE/'PG10420-role-code-trace-v1',data.BASE/'PG10422-role-code-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
APP,REPLAY,ORACLE = [PREFIX+'UserQuery'+n+'.java' for n in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
SPEC = 'evidence/01_PT/018_NK-OPS-001/2062_ResultCode15期待独立化・静的分類結果.md'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2063_RoleCode19最終SHA・選択source数追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10384-media-oracle-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10416-result-code-literal-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10414-result-code-six-compile-v1/manifest.json',
        '83e2904ee2a0ee50ef0efab4916f73f53aaa0660cd8b3a2555b2eec21477da35')
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['productTestsExecuted'] == 0
    assert proof['actualAssertionInvocationCounts'] is None
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes,raw):
    role = data.read_checked(data.BASE/'PG10398-role-view-preflight-v1/manifest.json',
        '61d668553986bcee00eba79234f5db7c2458ec153973d26db6a82519add35aa4')
    runtime = data.read_checked(data.BASE/'PG10402-role-view-post-v1/manifest.json',
        '08802be2aec7b9a6794526549d9cf9a19bbde0a0c979d253ec9908cc6ad40d93')
    cases = data.read_checked(data.BASE/'PG10398-role-view-preflight-v1/cases.json',role['casesSha256'])
    role_hashes = role['changedTestSourceHashes']
    assert role_hashes == runtime['sourceHashes'] and len(role_hashes) == 13
    code_hashes = proof['sourceHashes']
    assert len(code_hashes) == 6 and not set(role_hashes)&set(code_hashes)
    all_hashes = dict(role_hashes,**code_hashes)
    assert len(all_hashes) == 19 and all(hashes[p] == h for p,h in all_hashes.items())
    selected = {r['path'] for r in cases}
    assert len(cases) == runtime['tests'] == 4 and len(selected) == runtime['suites'] == 3
    assert selected <= set(role_hashes) and len(set(role_hashes)-selected) == 10
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 983
    index = {r['path']:r for r in rows}
    bindings = []
    for path,current_sha in sorted(all_hashes.items()):
        row = index[path]
        owner = row['canonicalOwner']
        assert row['owner'] == row['canonicalCostOwner'] == owner and owner != 'UNKNOWN'
        assert row['sha256'] != current_sha
        is_role = path in role_hashes
        proof_source = role['source'] if is_role else SOURCE
        proof_path = 'PG10398-role-view-preflight-v1' if is_role else 'PG10416-result-code-literal-post-v1'
        proof_sha = '61d668553986bcee00eba79234f5db7c2458ec153973d26db6a82519add35aa4' if is_role else PROOF
        subset = [r for r in cases if r['path'] == path]
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=current_sha,
            canonicalOwner=owner,canonicalCostOwner=owner,
            independentSpec='evidence/01_PT/015_NK-WEB-001/033_NK-WEB-001_Role期待値独立化・限定PT結果.md' if is_role else SPEC,
            sourceSpecificOracleMetadataProof=dict(source=proof_source,
                manifest=str((data.BASE/proof_path/'manifest.json').relative_to(ROOT)),sha256=proof_sha,
                qualification='ROLE_ORACLE_SOURCE_METADATA' if is_role else 'RESULT_CODE_ORACLE_SOURCE_METADATA',
                sharedReferenceNotAdditive=True,newGlobalSourceProductTestsExecuted=0,coverageMeasured=False,
                originalApiPtStatus='NOT_EXECUTED_HOLD' if not is_role else 'ONLY_SEPARATE_B98_FRAGMENT_EXECUTED',
                actualAssertionInvocationCounts=None),
            selectedRuntimeCasesOnOriginalB98Source=subset,selectedRuntimeMethodCount=len(subset),
            selectedRuntimeSource=runtime['source'] if subset else None,
            runtimeReassignedToNewGlobalSource=False,originalRuntimeProofReassigned=False,additionalSharedCostPp=0))
        row['sha256'] = current_sha
    assert len(bindings) == 19 and sum(r['selectedRuntimeMethodCount'] for r in bindings) == 4
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in all_hashes: adjusted['sha256'] = old['sha256']
        assert adjusted == old
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    assert len(logical) == 941
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    known = set(logical)|{r['path'] for r in rows}
    unknown = sorted(universe-known)
    assert len(universe) == 1810 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe-mains
    keep = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings','changedOracleTestBindings',
        'previousChangedOracleBindingsReference','changedResultProfileBindings','changedMediaOracleBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=[],newPathsAdded=0,
        changedRoleCodeOracleBindings=bindings,oldRowsChangedShaOnly=19,allOtherPriorRowsUnchanged=964,
        roleRuntimeQualification=dict(source=runtime['source'],manifest=str((data.BASE/'PG10402-role-view-post-v1/manifest.json').relative_to(ROOT)),
            sha256='08802be2aec7b9a6794526549d9cf9a19bbde0a0c979d253ec9908cc6ad40d93',
            changedSourceCount=13,selectedMethodCount=4,selectedSourceCount=3,unselectedSourceCount=10,
            selectedSources=sorted(selected),unselectedSources=sorted(set(role_hashes)-selected),
            runtimeReassignedToNewGlobalSource=False,additionalSharedCostPp=0),
        newLogicalCandidates=prior['newLogicalCandidates'],javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=len(mains&known),totalMain=len(mains),registeredTest=len(tests&known),totalTest=len(tests),
        unregisteredJavaPaths=unknown,legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        productTestsExecuted=0,actualAssertionInvocationCounts=None,newAccepted=0,formalUpdated=False,effortPercent=None,**keep)


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact source, independent metadata, original ownership/cost/runtime and UNKNOWN required')


def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousRoleCodeOracleRegistryReference' not in section
        section['previousRoleCodeOracleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentRoleCodeOracleMetadataBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedRoleCodeOracleBindings',count=19,
            qualification='ORACLE_METADATA_ONLY_ORIGINAL_PT_NOT_EXECUTED_HOLD')
        if name == SECTIONS[0]:
            section.update(javaPaths=value['javaPaths'],registered=value['registered'],unregistered=len(value['unregisteredJavaPaths']),
                main=dict(total=value['totalMain'],registered=value['registeredMain'],unregistered=value['totalMain']-value['registeredMain']),
                test=dict(total=value['totalTest'],registered=value['registeredTest'],unregistered=value['totalTest']-value['registeredTest']),
                independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(sourceRows=value['sourceCount'],newLogicalCandidates=value['newLogicalCandidates'],
                legacyOwnerLabelsDifferingFromCanonical=value['legacyOwnerLabelsDifferingFromCanonical'],
                guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    value = expected(prior,proof,hashes,raw)
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,wholeWbsAuditBefore=observed,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    _,_,pairs,spairs = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines: patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,hashes,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,hashes,raw)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    edits = [
        ('old-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='UNKNOWN')),
        ('new-cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-P014-01')),
        ('new-hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('current-hash',lambda v:v['changedRoleCodeOracleBindings'][0].update(sha256='0'*64)),
        ('false-pt',lambda v:v['changedRoleCodeOracleBindings'][0]['sourceSpecificOracleMetadataProof'].update(newGlobalSourceProductTestsExecuted=24)),
        ('false-coverage',lambda v:v['changedRoleCodeOracleBindings'][0]['sourceSpecificOracleMetadataProof'].update(coverageMeasured=True)),
        ('source',lambda v:v.update(source=prior['source'])),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('legacy-count',lambda v:v.update(legacyOwnerLabelsDifferingFromCanonical=0)),
        ('role-source-count-four',lambda v:v['roleRuntimeQualification'].update(selectedSourceCount=4)),
        ('role-source-count-all',lambda v:v['roleRuntimeQualification'].update(selectedSourceCount=13)),
        ('role-unselected-nine',lambda v:v['roleRuntimeQualification'].update(unselectedSourceCount=9)),
        ('role-runtime-new-source',lambda v:v['roleRuntimeQualification'].update(source=SOURCE)),
        ('role-runtime-transferred',lambda v:v['roleRuntimeQualification'].update(runtimeReassignedToNewGlobalSource=True)),
        ('acceptance',lambda v:v.update(newAccepted=1))]
    negatives = []
    for label,edit in edits:
        changed = copy.deepcopy(reference)
        edit(changed)
        try: contract(changed,reference)
        except ValueError: negatives.append(label)
        else: raise AssertionError('invalid metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=negatives,registered=value['registered'],total=value['javaPaths'],unknown=len(value['unregisteredJavaPaths']),
        allOtherPriorRowsUnchanged=964,oldRowsChangedShaOnly=19,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,originalRuntimeProofReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
