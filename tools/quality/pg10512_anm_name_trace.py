"""Single final source hash; keep every old runtime fragment on its original source."""
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
BASE = 'a55082a89'
SOURCE = '6612747b7a5492e5c49647d85cfc2dcbe6d75c9f'
PRIOR = 'af76f2b4671c12efbff4e95899ac0e2eed11395bc2e65129ba1529ae7e83de9f'
PROOF = '9b4846505a017402cdd65eefee11b35e2ca645228ebf55a7556fc8cbba79b809'
OUT = data.BASE/'PG10512-anm-name-trace-v1'
POST = data.BASE/'PG10514-anm-name-trace-post-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2077_ANM定数名是正・全method byte不変・追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10492-public-template-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10510-anm-type-name-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json',
        'bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5')
    assert normal['source'] == proof['source'] == SOURCE and normal['actualExit'] == proof['actualExit'] == normal['testsExecuted'] == proof['productTestsExecuted'] == 0
    assert proof['everyOtherClassByteIncludingAllMethodCodeAndDebugIdentical'] and proof['samePhysicalMainClasses'] == 1843
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','runtimeManifestSha256','correctedCasesSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    assert len(proof['sourceHashes']) == 1
    path,digest = next(iter(proof['sourceHashes'].items()))
    row, = [r for r in value['sourceRows'] if r['path'] == path]
    assert row['sha256'] != digest == hashes[path]
    assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P016-10'
    before = row['sha256']
    row['sha256'] = digest
    for old,new in zip(prior['sourceRows'],value['sourceRows']):
        adjusted = copy.deepcopy(new)
        if old['path'] == path:
            adjusted['sha256'] = old['sha256']
        assert adjusted == old
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentAnmNameMetadataBinding=dict(path=path,previousSha256=before,sha256=digest,
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
            proofSource=SOURCE,proofManifestSha256=PROOF,productTestsExecuted=0,
            qualification='IDENTIFIER_ONLY_EXACT_CLASS_UTF8_FIELD_ENTRY_CHANGE',
            originalControllerPtStatus='NOT_EXECUTED_HOLD',additionalSharedCostPp=0),
        originalA82TemplateRuntimeReassigned=False,original73ViewRuntimeReassigned=False)
    assert value['currentPublicTemplateRuntimeQualification']['source'] == prior['source'] != SOURCE
    assert value['currentPureViewRuntimeQualification']['source'] != SOURCE
    assert len(value['sourceRows']) == 983 and value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    return value


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('only one source SHA and naming metadata; all old runtime/cost/unknown unchanged')


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousAnmNameRegistryReference' not in section
        section['previousAnmNameRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentAnmNameMetadataBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentAnmNameMetadataBinding',
            qualification='SOURCE_AND_BINARY_METADATA_ONLY_NO_PT_OR_RUNTIME_REASSIGNMENT')
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
    prior,proof,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    value = expected(prior,proof,hashes)
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
        for before,after in lines:
            patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,hashes,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,hashes)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    edits = [
        ('owner',lambda v:v['currentAnmNameMetadataBinding'].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['currentAnmNameMetadataBinding'].update(additionalSharedCostPp=1)),
        ('current-sha',lambda v:v['currentAnmNameMetadataBinding'].update(sha256='0'*64)),
        ('false-pt',lambda v:v['currentAnmNameMetadataBinding'].update(productTestsExecuted=12)),
        ('old-a82-runtime-transfer',lambda v:v['currentPublicTemplateRuntimeQualification'].update(source=SOURCE)),
        ('old73-view-transfer',lambda v:v['currentPureViewRuntimeQualification'].update(source=SOURCE)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('old-source',lambda v:v.update(source=prior['source'])),
        ('acceptance',lambda v:v.update(newAccepted=1))]
    negatives = []
    for label,edit in edits:
        damaged = copy.deepcopy(reference)
        edit(damaged)
        try:
            contract(damaged,reference)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid source/runtime metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=negatives,registered=1808,total=1810,unknown=2,
        oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
