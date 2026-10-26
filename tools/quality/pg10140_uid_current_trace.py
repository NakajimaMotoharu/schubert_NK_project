"""Single existing Test hash/proof overlay; keep original owners, costs and historical rows."""
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
BASE = '9645b151e'
SOURCE = 'd17f122d2026b804be626bf7a3b76912923bd240'
TEST = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/LinuxInodeSecurityTest.java'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10140-uid-current-trace-v1'
POST = data.BASE/'PG10142-uid-current-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG10112-query-projection-trace-v1/manifest.json',
        '881f3117d2f980f94e493aa3c3d106aba26a8d0bba81d50043f0cb917bfb0728')
    proof = data.read_checked(data.BASE/'PG10136-uid-source-quality-post-v1/manifest.json',
        'f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29')
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE
    assert proof['currentTestSourceSha256'] == data.sha((ROOT/TEST).read_bytes())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,raw,snap


def contract(rows, prior):
    before = {r['path']:r for r in prior['sourceRows']}
    after = {r['path']:r for r in rows}
    if len(rows) != 976 or set(after) != set(before):
        raise ValueError('same976 paths')
    for path,row in after.items():
        if path != TEST:
            if row != before[path]: raise ValueError('other975 fields unchanged')
            continue
        if row['sha256'] != '2db25f5f5df6d21c472e20a181de43a7180aa36660ebbbd95c7bcb0e523f3253':
            raise ValueError('actual corrected Test hash')
        proof = row['currentLimitedSourceRuntimeProof']
        expected = dict(source=SOURCE,tests=1,suites=1,newTestIds=0,correctedExistingTestId='PT-DB-INBOX-125',
            manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10135-uid-oracle-post-v2/manifest.json',
            sha256='43685c265a5a73cc4a422ce75a7e52a795841282f2ff291dc16c1e7f70f2928d',
            wholeClassNotQualified=True,historicalProofReassigned=False)
        if proof != expected: raise ValueError('one-method source/run, not whole class')
        restored = copy.deepcopy(row)
        del restored['currentLimitedSourceRuntimeProof'],restored['currentIndependentSpec']
        restored['sha256'] = before[path]['sha256']
        if restored != before[path] or row['canonicalOwner'] != 'WBS-P003-05' or row['canonicalCostOwner'] != 'WBS-P003-05':
            raise ValueError('all prior responsibility/cost/history fields unchanged')


def metadata(raw,snap,value):
    inv = json.loads(raw)
    pairs = []
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths','currentChangedTestBindings',
            'currentChangedTestBindingReference','currentChangedTestBindingsInlineComplete')
        assert 'previousUidOracleRegistryOverlay' not in section
        section['previousUidOracleRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/004_NK-DAT-001/075_NK-DAT-001_UID期待値独立化実行結果.md',
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
    prior,proof,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    rows = copy.deepcopy(prior['sourceRows'])
    row = next(r for r in rows if r['path'] == TEST)
    row['sha256'] = proof['currentTestSourceSha256']
    row['currentIndependentSpec'] = 'evidence/01_PT/004_NK-DAT-001/074_NK-DAT-001_UID期待値独立化単体テスト仕様書.md'
    row['currentLimitedSourceRuntimeProof'] = dict(source=SOURCE,tests=1,suites=1,newTestIds=0,
        correctedExistingTestId='PT-DB-INBOX-125',manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10135-uid-oracle-post-v2/manifest.json',
        sha256='43685c265a5a73cc4a422ce75a7e52a795841282f2ff291dc16c1e7f70f2928d',wholeClassNotQualified=True,historicalProofReassigned=False)
    contract(rows,prior)
    value = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'unregisteredCurrentSourceBindings','unregisteredJavaPaths','newLogicalCandidates','registered','javaPaths',
        'registeredMain','totalMain','registeredTest','totalTest')}
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sourceRows=rows,sourceCount=976,
        changedTestBindings=[dict(path=TEST,source=SOURCE,sha256=row['sha256'],canonicalOwner='WBS-P003-05',canonicalCostOwner='WBS-P003-05',additionalAllocatedCostPp=0)],
        previousCurrentChangedTestBindingsReference=dict(manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10112-query-projection-trace-v1/manifest.json',
            sha256='881f3117d2f980f94e493aa3c3d106aba26a8d0bba81d50043f0cb917bfb0728',arrayPath='changedTestBindings',count=3),
        allOther975RowsUnchanged=True,newPathsAdded=0,newMethodIds=0,wholeWbsAuditBefore=observed,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    _,_,pairs,spairs = metadata(raw,snap,value)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines:
            patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,_,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    contract(value['sourceRows'],prior)
    after,asnap,_,_ = metadata(raw,snap,value)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    rows = value['sourceRows']
    i = next(i for i,r in enumerate(rows) if r['path'] == TEST)
    vectors = []
    for label,edit in (
        ('other-owner',lambda v:v[0].update(canonicalOwner='WBS-G13.07')),
        ('cost',lambda v:v[i].update(canonicalCostOwner='WBS-G13.07')),
        ('hash',lambda v:v[i].update(sha256='0'*64)),
        ('source',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(source='0'*40)),
        ('count',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(tests=9)),
        ('new-id',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(newTestIds=1)),
        ('whole-class',lambda v:v[i]['currentLimitedSourceRuntimeProof'].update(wholeClassNotQualified=False))):
        changed = copy.deepcopy(rows)
        edit(changed)
        try: contract(changed,prior)
        except ValueError: vectors.append(label)
        else: raise AssertionError('invalid row accepted')
    current = audit()
    assert current['actualExit'] == 1 and current['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),
        snapshotSha256=data.sha(asnap),metadataNegativeVectors=vectors,allOther975RowsUnchanged=True,
        registered=1801,total=1803,unknown=2,originalBudgetAndAcceptanceUnchanged=True,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=current,
        postHashInInventory=None,postHashNullReason='acyclic forward reference; this immutable manifest binds actual raw inventory hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
