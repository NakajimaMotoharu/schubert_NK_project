"""Two-path source overlay with distinct runtime sources and immutable historical responsibility."""
import copy
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate

ROOT = data.ROOT
BASE = 'ee40fb6f0'
SOURCE = '5e8255bcf8f309d05fb091cee2e9ad810b276c87'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10180-oracle-batch-trace-v1'
POST = data.BASE/'PG10182-oracle-batch-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
SUBJECTS = [dict(
    path='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/ServiceCredentialLocationTest.java',
    owner='WBS-P003-07',sha256='142442145de98b7c09bf0fc47db0aa9b8861b1613a14efa300d63c17179207bb',
    source='904ff094b89f457edb53a168f8495a0ad2e28ff9',tests=5,suites=1,wholeClassQualified=True,
    existingTestIds=['PT-OPS-CREDLOC-'+str(n).zfill(3) for n in range(1,6)],
    manifest='PG10160-credloc-oracle-post-v1',proofSha256='c6ff39eec87ae8728454862b7056bf24ce812ae8f37e48df61c5d03e8b5df910',
    spec='evidence/01_PT/018_NK-OPS-001/2032_Credential位置期待値独立化単体仕様.md'),dict(
    path='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/PayloadCodecTest.java',
    owner='WBS-P002-02',sha256='becfdcb277f693d7f8f70a06e1b5a32361d84856314a66f2116625d80b264970',
    source=SOURCE,tests=1,suites=1,wholeClassQualified=False,
    existingTestIds=['PT-PRO-002-E01','PT-PRO-002-E02','PT-PRO-002-P02'],
    manifest='PG10174-cancel-wire-post-v1',proofSha256='f27db4ecb8fd113e713e5d28b37c849077b4256dee3ce2bdbdb99bee13766fbc',
    spec='evidence/01_PT/002_NK-PRO-002/022_取消状態別独立wire補強仕様.md')]


def runtime(subject):
    return dict(source=subject['source'],tests=subject['tests'],suites=subject['suites'],newTestIds=0,
        existingTestIds=subject['existingTestIds'],wholeClassQualified=subject['wholeClassQualified'],
        manifest=str((data.BASE/subject['manifest']/'manifest.json').relative_to(ROOT)),sha256=subject['proofSha256'],
        historicalProofReassigned=False,separateSourcesNotUnion=True)


def inputs():
    prior = data.read_checked(data.BASE/'PG10140-uid-current-trace-v1/manifest.json',
        '59a924c4a3da6ce35c141b762425d8375d946c12bd3cbf5988106f09385616fe')
    normal = data.read_checked(data.BASE/'PG10169-cancel-six-compile-v2/manifest.json',
        '1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    for subject in SUBJECTS:
        proof = data.read_checked(data.BASE/subject['manifest']/'manifest.json',subject['proofSha256'])
        assert proof['actualExit'] == 0 and proof['source'] == subject['source']
        assert (proof['tests'],proof['suites'],proof['newTestIds']) == (subject['tests'],1,0)
        assert hashes[subject['path']] == subject['sha256']
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,raw,snap


def contract(rows,prior):
    old = {r['path']:r for r in prior['sourceRows']}
    after = {r['path']:r for r in rows}
    subjects = {r['path']:r for r in SUBJECTS}
    if len(rows) != 976 or set(old) != set(after): raise ValueError('same976 paths')
    for path,row in after.items():
        if path not in subjects:
            if row != old[path]: raise ValueError('other974 all fields immutable')
            continue
        subject = subjects[path]
        if row['sha256'] != subject['sha256'] or row['currentIndependentSpec'] != subject['spec']:
            raise ValueError('actual current hash and independent spec')
        if row['currentLimitedSourceRuntimeProof'] != runtime(subject):
            raise ValueError('distinct actual source/run/counters, no union')
        restored = copy.deepcopy(row)
        del restored['currentLimitedSourceRuntimeProof'],restored['currentIndependentSpec']
        restored['sha256'] = old[path]['sha256']
        if restored != old[path] or row['canonicalOwner'] != subject['owner'] or row['canonicalCostOwner'] != subject['owner']:
            raise ValueError('original ownership/cost/history immutable')


def metadata(raw,snap):
    inv = json.loads(raw)
    pairs = []
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths','currentChangedTestBindings',
            'currentChangedTestBindingReference','currentChangedTestBindingsInlineComplete')
        assert 'previousOracleTwoPathRegistryOverlay' not in section
        section['previousOracleTwoPathRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2035_期待値是正二Test追跡結果.md',
            currentAddedTestPaths=[],currentChangedTestBindings=[],currentChangedTestBindingsInlineComplete=False,
            currentChangedTestBindingReference=dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
                sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedTestBindings',count=2,source=SOURCE))
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
    prior,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    rows = copy.deepcopy(prior['sourceRows'])
    by_path = {r['path']:r for r in rows}
    for subject in SUBJECTS:
        row = by_path[subject['path']]
        assert 'currentLimitedSourceRuntimeProof' not in row and 'currentIndependentSpec' not in row
        row.update(sha256=subject['sha256'],currentIndependentSpec=subject['spec'],currentLimitedSourceRuntimeProof=runtime(subject))
    contract(rows,prior)
    kept = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'unregisteredCurrentSourceBindings','unregisteredJavaPaths','newLogicalCandidates','registered','javaPaths',
        'registeredMain','totalMain','registeredTest','totalTest')}
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sourceRows=rows,sourceCount=976,
        changedTestBindings=[dict(path=s['path'],source=SOURCE,sha256=s['sha256'],canonicalOwner=s['owner'],
            canonicalCostOwner=s['owner'],actualRuntimeSource=s['source'],additionalAllocatedCostPp=0) for s in SUBJECTS],
        previousCurrentChangedTestBindingsReference=dict(manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10140-uid-current-trace-v1/manifest.json',
            sha256='59a924c4a3da6ce35c141b762425d8375d946c12bd3cbf5988106f09385616fe',arrayPath='changedTestBindings',count=1),
        allOther974RowsUnchanged=True,newPathsAdded=0,newMethodIds=0,wholeWbsAuditBefore=observed,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,**kept))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,raw,snap = inputs()
    _,_,pairs,spairs = metadata(raw,snap)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines: patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    contract(value['sourceRows'],prior)
    after,asnap,_,_ = metadata(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    rows = value['sourceRows']
    i = next(i for i,r in enumerate(rows) if r['path'] == SUBJECTS[-1]['path'])
    vectors = []
    for label,edit in (
        ('other-owner',lambda v:v[0].update(canonicalOwner='WBS-G13.07')),
        ('cost',lambda v:v[i].update(canonicalCostOwner='WBS-G13.07')),
        ('hash',lambda v:v[i].update(sha256='0'*64)),
        ('source',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(source=SUBJECTS[0]['source'])),
        ('count',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(tests=5)),
        ('new-id',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(newTestIds=1)),
        ('whole-class',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(wholeClassQualified=True))):
        changed = copy.deepcopy(rows)
        edit(changed)
        try: contract(changed,prior)
        except ValueError: vectors.append(label)
        else: raise AssertionError('invalid registry accepted')
    current = audit()
    assert current['actualExit'] == 1 and current['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=vectors,allOther974RowsUnchanged=True,registered=1801,total=1803,unknown=2,
        originalBudgetAndAcceptanceUnchanged=True,runtimeSourcesSeparate=True,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=current,
        postHashInInventory=None,postHashNullReason='acyclic forward reference; immutable post binds actual raw inventory hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
