"""Registry v2: ten existing Test SHA edits only, other982 rows and all owner/cost/runtime fields retained."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced, SECTIONS, INV, SNAP
from pg9338_wbs_reference_metadata_post import validate

SOURCE = '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
OUT = data.BASE/'PG13086-monitor-test-trace-v1'
POST = data.BASE/'PG13087-monitor-test-trace-post-v1'
PRIOR = data.BASE/'PG13064-time-header-trace-v1/manifest.json'
PRIOR_SHA = 'c4c5813ec7ec4e5abe50c3ae1f7670173129f977e5e0968fd709883fe42b9f3c'
PROOF_SHA = '911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc'
MARKER = 'previousMonitorTestNamesPG13086Reference'
EDITED = ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/AsyncQueueMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BackupHealthMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/DlqHealthMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/ExpiryBacklogMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/IntegrityHealthMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/RestartHealthMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/TimedDbPoolMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/TimedSyncLatencyMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/TransferHealthMonitorTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/WebLogBacklogMonitorTest.java']

def inputs():
    prior = data.read_checked(PRIOR,PRIOR_SHA)
    before = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json','fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    n = data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json','77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932')
    p = data.read_checked(data.BASE/'PG13082-monitor-test-post-v1/manifest.json',PROOF_SHA)
    c = data.read_checked(data.BASE/'PG13084-monitor-test-context-v1/manifest.json','172f097d528028d906b5e012a43d413b067f5b0e4c360c8ce2163c0032328125')
    assert prior['source'] == before['source'] == '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
    assert n['source'] == p['source'] == c['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == c['actualExit'] == 0
    assert not p['selectedMainCoverage100'] and len(p['monitorGroups']) == 10 and all(v['coverage100'] for v in p['monitorGroups'].values()) and p['rawStatic'] == 20 and p['staticGateExit'] == 1 and p['spotbugsSixExit'] == 0
    assert p['observedTestExecutions'] == 81 and p['allMainClassesUnchanged'] == 1843 and p['oldTestPhysicalUnchanged'] == 1961 and p['changedTestPhysical'] == 11 and p['newTestPhysical'] == 0
    assert c['sourceDerivedRaw'] == 8461 and c['totalPriorCorrections'] == 964
    hashes = n['begin']['inputHashes']; old = before['begin']['inputHashes']
    assert set(hashes) == set(old) and {path for path in hashes if hashes[path] != old[path]} == set(EDITED)
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert len(prior['sourceRows']) == 992 and all(old[row['path']] == row['sha256'] for row in prior['sourceRows'])
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,hashes,raw,snap

def edited_rows(prior,hashes):
    rows = copy.deepcopy(prior['sourceRows']); seen = []
    for row in rows:
        if row['path'] in set(EDITED):
            assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P018-09'
            assert row['sha256'] != hashes[row['path']]
            row['sha256'] = hashes[row['path']]; seen.append(row['path'])
    assert set(seen) == set(EDITED) and len(seen) == 10
    return rows

def require(value,prior,proof,hashes):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == edited_rows(prior,hashes) and len(value['sourceRows']) == value['sourceCount'] == 992
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8461 and value['totalPriorCorrections'] == 964 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['selectedMain'] == proof['selectedMain'] and value['currentQualification']['selectedMainCoverage100'] == proof['selectedMainCoverage100']
    assert value['currentQualification']['observedTestExecutions'] == 81 and value['currentQualification']['rawStaticScope'] == 20
    assert value['registered'] == 1817 and value['javaPaths'] == 1819 and value['newPathsAdded'] == 0

def main():
    invocation = capture(__file__); assert not OUT.exists(); prior,proof,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    rows = edited_rows(prior,hashes)
    registered = universe & ({row['path'] for row in json.loads(raw)['artifacts']} | {row['path'] for row in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1819 and len(registered) == 1817 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=992,registered=1817,javaPaths=1819,registeredMain=965,totalMain=965,registeredTest=852,totalTest=854,
        unregisteredJavaPaths=unknown,newPathsAdded=0,newTestPaths=[],editedSourcePaths=list(EDITED),existingShaOnlyEdits=10,
        original982OtherRowsAllFieldsPreserved=True,ownersCostsAndHistoricalFieldsUnchanged=True,
        newLogicalCandidates=sum(row.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for row in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(row.get('legacyReportedOwner') != row['canonicalOwner'] for row in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=81,newTestIds=0,suites=10,
            selectedMain=proof['selectedMain'],selectedMainCoverage100=proof["selectedMainCoverage100"],monitorGroups=proof["monitorGroups"],allTenMonitorGroupsCoverage100=True,rawStaticScope=20,staticGateExit=1,spotbugsSixExit=0,
            allMainPhysicalClasses=1843,mainChangedPhysical=0,allOtherMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1961,changedTestPhysical=11,newTestPhysical=0,fullArtifactCoverage100=False),
        sourceDerivedRaw=8461,mainRaw=1504,testRaw=6957,totalPriorCorrections=964,actualViolationCount=None,
        removedFindingIds=['PMD-04704', 'PMD-04707', 'PMD-04812', 'PMD-04815', 'PMD-04834', 'PMD-04890', 'PMD-04893', 'PMD-04903', 'PMD-04906', 'PMD-04907', 'PMD-04917'],inheritedFlatScopeCountersCopied=False,oldRuntimeDomainsReachableViaImmutablePriorReference=True,
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    require(value,prior,proof,hashes); verify(invocation); OUT.mkdir(); data.write(OUT/'manifest.json',value)
    print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name]; assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2413_監視Test十_命名・fixture規約是正結果.md',currentAddedTestPaths=[],currentEditedSourcePaths=list(EDITED))
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1819,registered=1817,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=854,registered=852,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=992,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def emit():
    _,_,_,raw,snap = inputs(); assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,after_snap = documents(raw,snap); patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,after_snap)]:
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__); assert not POST.exists(); prior,proof,hashes,raw,snap = inputs()
    m = json.loads((OUT/'manifest.json').read_bytes()); require(m,prior,proof,hashes)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actual_raw,actual_snap,json.loads(raw),json.loads(snap)); assert (actual_raw,actual_snap) == documents(raw,snap)
    labels = []
    for label,change in [('owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-F03')),
        ('old-row-sha',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('source',lambda v:v.update(source='0'*40)),
        ('acceptance',lambda v:v.update(newAccepted=1)),('legacy-runtime',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),
        ('raw',lambda v:v.update(sourceDerivedRaw=8474)),('corrections',lambda v:v.update(totalPriorCorrections=951)),
        ('fake-new-path',lambda v:v.update(newPathsAdded=1))]:
        bad = copy.deepcopy(m); change(bad); assert bad != m
        try: require(bad,prior,proof,hashes)
        except AssertionError: labels.append(label)
        else: raise AssertionError('wrong current source/owner/row accepted')
    observed = audit(); assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,existingShaOnlyEdits=10,original982OtherRowsAllFieldsPreserved=True,
        registered=1817,javaPaths=1819,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
