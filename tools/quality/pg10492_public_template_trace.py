"""Six final hashes, current14-template fragment and source-derived ownership correction."""
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
from pg10420_role_code_trace import INV, SNAP, SECTIONS

ROOT = data.ROOT
BASE = '494fafd56'
SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
PRIOR = '830369ea7b19ae29d82905852d2c564ba7eb702022b627da58fe7394a52119d7'
PROOF = '1c4458f2db226efc0ffeb32bbbdaada06c7a25fd75b22fc7f03abe619f76beeb'
RUNTIME = 'aa8a78752abe9812c244579d8e3303359c9fafd6a979cd1f5a775ffd7a014871'
OUT = data.BASE/'PG10492-public-template-trace-v1'
POST = data.BASE/'PG10494-public-template-trace-post-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2075_公開template14method・六最終SHA・主担当訂正結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10470-topbar-contract-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10482-disjoint-six-literal-post-v1/manifest.json',PROOF)
    runtime = data.read_checked(data.BASE/'PG10490-public-template-post-v1/manifest.json',RUNTIME)
    prepared = data.read_checked(data.BASE/'PG10486-public-template-preflight-v1/manifest.json',
        '781f1048b32a310e8d5b961116c5e5268e33e3625d4e472ce3dd23e9979666d4')
    normal = data.read_checked(data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json',
        '11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179')
    assert all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (proof,runtime,prepared,normal))
    assert normal['testsExecuted'] == proof['productTestsExecuted'] == 0
    assert runtime['tests'] == 14 and runtime['suites'] == 2 and runtime['sourceHashes'] == prepared['changedTestSourceHashes']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    cases = data.read_checked(data.BASE/'PG10486-public-template-preflight-v1/cases.json',prepared['casesSha256'])
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,runtime,cases,hashes,raw,snap


def expected(prior,proof,runtime,cases,hashes,raw):
    assert len(cases) == 14 and len({(r['className'],r['method'],r['testId']) for r in cases}) == 14
    selected = {r['path'] for r in cases}
    changed = proof['sourceHashes']
    assert len(changed) == 6 and selected == set(runtime['sourceHashes']) and selected <= set(changed)
    rows = copy.deepcopy(prior['sourceRows'])
    index = {r['path']:r for r in rows}
    assert len(rows) == len(index) == 983
    corrected = []
    for case in cases:
        row = index[case['path']]
        assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] != 'UNKNOWN'
        assert hashes[case['path']] == case['sourceSha256'] == runtime['sourceHashes'][case['path']]
        assert case['canonicalOwner'] != row['canonicalOwner']
        update = copy.deepcopy(case)
        update.update(canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
            originalReportedOwner=case['canonicalOwner'],originalRelatedWbsReference=case['canonicalOwner'],
            correctionBug='BUG-1836',correctionYkt='YKT-1587',additionalSharedCostPp=0)
        assert {k:update[k] for k in case if k != 'canonicalOwner'} == {k:v for k,v in case.items() if k != 'canonicalOwner'}
        corrected.append(update)
    assert {r['canonicalOwner'] for r in corrected} == {'WBS-P016-08','WBS-P016-11'}
    bindings = []
    for path,digest in sorted(changed.items()):
        row = index[path]
        assert hashes[path] == digest != row['sha256']
        assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] != 'UNKNOWN'
        subset = [r for r in corrected if r['path'] == path]
        assert all(r['canonicalOwner'] == row['canonicalOwner'] for r in subset)
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=digest,
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
            sourceOnlyProof=dict(source=SOURCE,manifestSha256=PROOF,productTestsExecuted=0,
                qualification='SAME_VALUE_CONSTANTS_AND_ALL_ORIGINAL_TOKENS_VERIFIED'),
            currentSourceRuntimeFragment=dict(source=SOURCE,manifestSha256=RUNTIME,cases=subset,
                productTestsExecuted=len(subset),additionalSharedCostPp=0,wholeJavaCoverage100=False,
                qualification='EXACT_PUBLIC_TEMPLATE_METHODS_ONLY' if subset else 'NOT_EXECUTED_HOLD',
                originalDynamicDependenciesReplaced=False)))
        row['sha256'] = digest
    assert sum(len(b['currentSourceRuntimeFragment']['cases']) for b in bindings) == 14
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in changed:
            adjusted['sha256'] = old['sha256']
        assert adjusted == old
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    known = set(index)|{r['path'] for r in json.loads(raw)['artifacts']}
    assert len(universe) == prior['javaPaths'] == 1810 and sorted(universe-known) == prior['unregisteredJavaPaths']
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key)
    value.update(source=SOURCE,sourceRows=rows,oldRowsChangedShaOnly=6,allOtherPriorRowsUnchanged=977,
        changedDisjointLiteralBindings=bindings,correctedPublicTemplateCases=corrected,
        caseOwnerCorrection=dict(originalManifest='PG10486-public-template-preflight-v1/cases.json',correctedCases=14,
            originalRawMetadataPreserved=True,classMethodTestIdSourceHashUnchanged=True,
            logicalReferencesNotCanonicalCostOwners=True,additionalSharedCostPp=0),
        currentPublicTemplateRuntimeQualification=dict(source=SOURCE,manifestSha256=RUNTIME,
            selectedMethodCount=14,selectedSourceCount=2,completeMainClassesMeasured=14,
            wholeJavaCoverage100=False,oldExecUnion=False,newTestIds=0,newAccepted=0),
        prior73ViewCoverageAndRuntimeReassigned=False)
    return value


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact source/corrected case ownership/historical proof and UNKNOWN required')


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousPublicTemplateRegistryReference' not in section
        section['previousPublicTemplateRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentDisjointLiteralBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedDisjointLiteralBindings',count=6,
            qualification='SIX_SOURCE_METADATA_ONLY_TWO_TEMPLATE_RUNTIME_FRAGMENTS')
        section['currentPublicTemplateCaseOwnerCorrectionReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='correctedPublicTemplateCases',count=14,
            canonicalOwnerDerivedFromSourceRows=True,additionalSharedCostPp=0)
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,runtime,cases,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    value = expected(prior,proof,runtime,cases,hashes,raw)
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'corrected-cases.json',value['correctedPublicTemplateCases'])
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,runtimeManifestSha256=RUNTIME,
        correctedCasesSha256=data.sha((OUT/'corrected-cases.json').read_bytes()),wholeWbsAuditBefore=observed,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,_,_,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    _,_,pairs,spairs = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines:
            patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,runtime,cases,hashes,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,runtime,cases,hashes,raw)
    contract(value,reference)
    assert data.read_checked(OUT/'corrected-cases.json',value['correctedCasesSha256']) == reference['correctedPublicTemplateCases']
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    edits = [
        ('owner',lambda v:v['sourceRows'][0].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['changedDisjointLiteralBindings'][0].update(canonicalCostOwner='WBS-P014-01')),
        ('current-hash',lambda v:v['changedDisjointLiteralBindings'][0].update(sha256='0'*64)),
        ('case-original-wrong-owner',lambda v:v['correctedPublicTemplateCases'][0].update(canonicalOwner=cases[0]['canonicalOwner'])),
        ('case-test-id',lambda v:v['correctedPublicTemplateCases'][0].update(testId='PT-SCR-999')),
        ('false-runtime28',lambda v:v['currentPublicTemplateRuntimeQualification'].update(selectedMethodCount=28)),
        ('false-coverage',lambda v:v['currentPublicTemplateRuntimeQualification'].update(wholeJavaCoverage100=True)),
        ('old73-runtime-transfer',lambda v:v['currentPureViewRuntimeQualification'].update(source=SOURCE)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('source',lambda v:v.update(source=prior['source'])),
        ('new-path',lambda v:v.update(newPathsAdded=1)),
        ('acceptance',lambda v:v.update(newAccepted=1)),
        ('additional-cost',lambda v:v['caseOwnerCorrection'].update(additionalSharedCostPp=1))]
    negatives = []
    for label,edit in edits:
        changed = copy.deepcopy(reference)
        edit(changed)
        try:
            contract(changed,reference)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        correctedCasesSha256=value['correctedCasesSha256'],metadataNegativeVectors=negatives,
        registered=1808,total=1810,unknown=2,allOtherPriorRowsUnchanged=977,oldRowsChangedShaOnly=6,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,originalRuntimeProofReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
