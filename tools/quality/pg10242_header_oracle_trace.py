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
BASE = '28844bd2e'
SOURCE = 'ddde23ca0304654d59608b434c647c87d58ae3b6'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10242-header-oracle-trace-v1'
POST = data.BASE/'PG10244-header-oracle-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
SUBJECTS = [dict(
    path='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/MessageCodecTest.java',
    owner='WBS-P002-03',sha256='65e12cc4b54b26c0730e868925a88bc0f335061113d3b77cb90f4a9e195f23ca',
    source=SOURCE,tests=1,suites=1,wholeClassQualified=False,
    existingTestIds=['PT-PRO-002-H01'],
    manifest='PG10232-header-profile-post-v1',proofSha256='4a1660819973d2a676f02d92db21ac52a246ff225bd0fc773e7438a641dd6166',
    spec='evidence/01_PT/002_NK-PRO-002/026_応答・event独立header期待値補強仕様.md')]


def runtime(subject):
    return dict(source=subject['source'],tests=subject['tests'],suites=subject['suites'],newTestIds=0,
        existingTestIds=subject['existingTestIds'],wholeClassQualified=subject['wholeClassQualified'],
        manifest=str((data.BASE/subject['manifest']/'manifest.json').relative_to(ROOT)),sha256=subject['proofSha256'],
        historicalProofReassigned=False,separateSourcesNotUnion=True)


def inputs():
    prior = data.read_checked(data.BASE/'PG10214-pre-sql-trace-v1/manifest.json',
        '108ef62af63e0857508b7e64b3e2d9d510d10033ebed712772772da7bb7ff16f')
    normal = data.read_checked(data.BASE/'PG10226-header-profile-six-compile-v1/manifest.json',
        'ffb1b71ad14efa4b8921c58a19541728243e35d60f873983528bce177b914b9c')
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
    if len(rows) != 979 or set(old) != set(after): raise ValueError('same979 paths')
    for path,row in after.items():
        if path not in subjects:
            if row != old[path]: raise ValueError('other978 all fields immutable')
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
        assert 'previousHeaderOracleOnePathRegistryOverlay' not in section
        section['previousHeaderOracleOnePathRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2040_Header独立期待値一Test追跡結果.md',
            currentAddedTestPaths=[],currentChangedTestBindings=[],currentChangedTestBindingsInlineComplete=False,
            currentChangedTestBindingReference=dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
                sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedTestBindings',count=1,source=SOURCE))
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sourceRows=rows,sourceCount=979,
        changedTestBindings=[dict(path=s['path'],source=SOURCE,sha256=s['sha256'],canonicalOwner=s['owner'],
            canonicalCostOwner=s['owner'],actualRuntimeSource=s['source'],additionalAllocatedCostPp=0) for s in SUBJECTS],
        previousCurrentChangedTestBindingsReference=dict(manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10214-pre-sql-trace-v1/manifest.json',
            sha256='108ef62af63e0857508b7e64b3e2d9d510d10033ebed712772772da7bb7ff16f',arrayPath='changedTestBindings',count=1),
        allOther978RowsUnchanged=True,newPathsAdded=0,newMethodIds=0,wholeWbsAuditBefore=observed,
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
        ('source',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(source='0'*40)),
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
        metadataNegativeVectors=vectors,allOther978RowsUnchanged=True,registered=1804,total=1806,unknown=2,
        originalBudgetAndAcceptanceUnchanged=True,runtimeSourcesSeparate=True,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=current,
        postHashInInventory=None,postHashNullReason='acyclic forward reference; immutable post binds actual raw inventory hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
