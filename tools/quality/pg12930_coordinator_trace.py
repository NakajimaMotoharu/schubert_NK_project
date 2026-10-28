"""Add one explicit business Test owner, preserving all original rows/acceptance/history."""
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

SOURCE = '4a3fad244f21530547fdc79b16f9ea3af0ca13af'
OUT = data.BASE/'PG12930-coordinator-trace-v1'
POST = data.BASE/'PG12931-coordinator-trace-post-v1'
PROOF = 'b3904e8e05c97c403ff65e65793dae5d3e447c564c61cbd7150262e7041ea3f9'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsRequestReplyCleanupTest.java'
MARKER = 'previousCoordinatorPG12930Reference'

def inputs():
    prior = data.read_checked(data.BASE/'PG12902-reply-terminal-trace-v1/manifest.json', 'abc790d1356a461040d3dfe52c9db8ffb1cf9f6736a3ee200db4cb74c1d68590')
    proof = data.read_checked(data.BASE/'PG12926-coordinator-corrected-post-v1/manifest.json', PROOF)
    normal = data.read_checked(data.BASE/'PG12920-coordinator-corrected-six-compile-v1/manifest.json', '14e6f1dce556fe58dc1ecdea73c0b65ab6dbc45d82625601eae1732378e239cc')
    assert proof['source'] == normal['source'] == SOURCE and proof['actualExit'] == normal['actualExit'] == 0
    assert proof['observedTestExecutions'] == 17 and proof['selectedFiveMainCoverage100'] and proof['newTestPhysical'] == 2
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,hashes,raw,snap

def reference(prior, proof, hashes, raw):
    value = copy.deepcopy(prior)
    for k in ['actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore']: value.pop(k,None)
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    subjects = ['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'+x+'.java' for x in ['JmsRequestReplyClient','JmsRequestReplyException','ReplyCorrelationRegistry','PendingReply','JmsRequestSender']]
    changed_path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsRequestReplyClientTest.java'
    plan = data.read_checked(data.BASE/'PG12918-coordinator-corrected-plan-v1/manifest.json','3491b6d92468eee54d6aba15e1efe500fa82676ac5bdc4bdfdcf53fbe58953c3')
    change = [x for x in plan['sourceChanges'] if x['path'] == changed_path][0]
    assert len(value['sourceRows']) == 984
    for oldrow in value['sourceRows']:
        if oldrow['path'] == changed_path:
            assert oldrow['sha256'] == change['beforeSha256'] and oldrow['canonicalOwner'] == oldrow['canonicalCostOwner'] == 'WBS-P005-02'
            oldrow['sha256'] = hashes[changed_path]
        else:
            assert hashes[oldrow['path']] == oldrow['sha256']
    assert all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P005-02' for p in subjects)
    assert TEST not in logical and TEST not in {r['path'] for r in value['sourceRows']}
    row = dict(path=TEST,sha256=hashes[TEST],owner='WBS-P005-02',canonicalOwner='WBS-P005-02',canonicalCostOwner='WBS-P005-02',
        changeOwner='WBS-P005-02',basis='2393_SS321_6_9_FAILURE_IDENTITY_CAPACITY_RECOVERY_BUFFER_ORACLES',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec='evidence/01_PT/018_NK-OPS-001/2393_P005同期失敗後回復_単体テスト仕様書.md',
        methodTestIds=['PT-JMS-RECOVERY-001','PT-JMS-RECOVERY-002','PT-JMS-RECOVERY-003','PT-JMS-RECOVERY-004'],mainSourceSubjects=subjects,
        ownerProofManifest=str((data.BASE/'PG12926-coordinator-corrected-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF)
    rows = value['sourceRows']+[row]
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & (set(logical)|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1812 and len(registered) == 1810 and unknown == prior['unregisteredJavaPaths']
    assert len(rows) == len({r['path'] for r in rows}) == 985
    value.update(source=SOURCE,sourceRows=rows,sourceCount=985,registered=1810,javaPaths=1812,registeredMain=965,totalMain=965,
        registeredTest=845,totalTest=847,newPathsAdded=1,newTestPaths=[TEST],
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentCoordinatorRecoveryBinding=dict(source=SOURCE,newTest=row,original984RowsChangedShaOnly=1,additionalSharedCostPp=0),
        currentCoordinatorRecoveryQualification=dict(source=SOURCE,proofManifestSha256=PROOF,observedTestExecutions=17,newTestIds=4,suites=3,
            selectedFiveMain=proof['selectedFiveMain'],selectedFiveMainCoverage100=True,completeArtifactCounters=proof['completeArtifactCounters'],
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1961,changedOldTestPhysical=2,newTestPhysical=2,rawStatic=9,staticGateExit=1,spotbugsSixExit=0,
            oldExecUnion=False,newAccepted=0,whole451Accepted=False))
    assert value['newLogicalCandidates'] == prior['newLogicalCandidates']+1
    return value

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name]; assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2394_P005同期失敗後回復_実行結果.md',currentAddedTestPaths=[TEST])
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1812,registered=1810,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=847,registered=845,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=985,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def main():
    invocation = capture(__file__); assert not OUT.exists()
    prior,proof,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    before = audit(); assert before['actualExit'] == 1
    value = reference(prior,proof,hashes,raw); verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=before,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def emit():
    _,_,_,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap = documents(raw,snap); patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,asnap)]:
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__); assert not POST.exists()
    prior,proof,hashes,raw,snap = inputs(); m = json.loads((OUT/'manifest.json').read_bytes())
    expected = reference(prior,proof,hashes,raw)
    assert all(m.get(k) == v for k,v in expected.items())
    before_rows = {x['path']:x for x in prior['sourceRows']}
    after_rows = {x['path']:x for x in m['sourceRows'][:-1]}
    assert set(before_rows) == set(after_rows) and m['newAccepted'] == 0
    differences = [p for p in before_rows if before_rows[p] != after_rows[p]]
    assert differences == ['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsRequestReplyClientTest.java']
    p = differences[0]
    assert {k:v for k,v in before_rows[p].items() if k != 'sha256'} == {k:v for k,v in after_rows[p].items() if k != 'sha256'}
    actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actualraw,actualsnap,json.loads(raw),json.loads(snap))
    assert (actualraw,actualsnap) == documents(raw,snap)
    current = json.loads(actualraw)
    assert all(current[name]['currentAddedTestPaths'] == [TEST] for name in SECTIONS)
    result = audit(); assert result['actualExit'] == 1 and not result['passed']
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),original984RowsChangedShaOnly=1,
        newTestCanonicalOwner='WBS-P005-02',newTestCanonicalCostOwner='WBS-P005-02',registered=1810,javaPaths=1812,
        unknownPathsUnchanged=2,wholeWbsAudit=result,whole451Accepted=False,newAccepted=0,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),productTestsExecuted=0))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
