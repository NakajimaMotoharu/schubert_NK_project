"""One final Test SHA plus independent ten-method qualification; historical runtime preserved."""
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
BASE = 'a55c9bde3'
SOURCE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
PRIOR = 'b93037871e0227b4d3c699e290973d846e9cb7dd5808aa59d0415b219ae8bb93'
PROOF = 'a637d6413ebeca101bb3aa091a7210034309f2cf3f1dbf174ef02dbef657f7cc'
OUT = data.BASE/'PG10566-trace-context-registry-v1'
POST = data.BASE/'PG10568-trace-context-registry-post-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2084_REQ006Context補完・当十PT・完全五class適用counter閉鎖結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10512-anm-name-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10564-trace-context-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    assert normal['source'] == proof['source'] == SOURCE
    assert normal['actualExit'] == proof['actualExit'] == normal['testsExecuted'] == 0
    assert proof['tests'] == 10 and proof['suites'] == 1 and proof['allFiveApplicableCountersNoMisses']
    assert proof['mainClassesUnchanged'] == 1843 and proof['otherTestClassesUnchanged'] == 1960
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    assert len(proof['sourceHashes']) == 1
    path,digest = next(iter(proof['sourceHashes'].items()))
    assert path.endswith('/WebRequestTraceTest.java')
    row, = [r for r in value['sourceRows'] if r['path'] == path]
    assert row['sha256'] != digest == hashes[path]
    assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P006-03'
    before = row['sha256']
    row['sha256'] = digest
    for old,new in zip(prior['sourceRows'],value['sourceRows']):
        adjusted = copy.deepcopy(new)
        if old['path'] == path:
            adjusted['sha256'] = old['sha256']
        assert adjusted == old
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentTraceContextRuntimeQualification=dict(source=SOURCE,path=path,previousSha256=before,sha256=digest,
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
            proofManifestSha256=PROOF,tests=10,suites=1,completeMainClasses=5,
            allApplicableCountersNoMisses=True,productSourceMainClassesUnchanged=1843,
            coverageByCompleteSelectedClass=copy.deepcopy(proof['coverageByCompleteSelectedClass']),
            jacocoSession=copy.deepcopy(proof['jacocoSession']),whole451Accepted=False,
            additionalSharedCostPp=0,oldRuntimeReassigned=False))
    assert value['currentPublicTemplateRuntimeQualification'] == prior['currentPublicTemplateRuntimeQualification']
    assert value['currentPureViewRuntimeQualification'] == prior['currentPureViewRuntimeQualification']
    assert value['currentAnmNameMetadataBinding'] == prior['currentAnmNameMetadataBinding']
    assert len(value['sourceRows']) == 983 and value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    return value


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('only one source SHA and naming metadata; all old runtime/cost/unknown unchanged')


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousTraceContextRegistryReference' not in section
        section['previousTraceContextRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentTraceContextRuntimeQualificationReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentTraceContextRuntimeQualification',
            qualification='EXACT_TEN_METHOD_CURRENT_RUN_AND_FIVE_COMPLETE_MAIN_NOT_WHOLE_451')
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
        ('owner',lambda v:v['currentTraceContextRuntimeQualification'].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['currentTraceContextRuntimeQualification'].update(additionalSharedCostPp=1)),
        ('current-sha',lambda v:v['currentTraceContextRuntimeQualification'].update(sha256='0'*64)),
        ('false-pt-count',lambda v:v['currentTraceContextRuntimeQualification'].update(tests=11)),
        ('old-a82-runtime-transfer',lambda v:v['currentPublicTemplateRuntimeQualification'].update(source=SOURCE)),
        ('old73-view-transfer',lambda v:v['currentPureViewRuntimeQualification'].update(source=SOURCE)),
        ('old661-name-transfer',lambda v:v['currentAnmNameMetadataBinding'].update(proofSource=SOURCE)),
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
