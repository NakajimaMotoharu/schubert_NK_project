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

SOURCE = '5590eee0d766fdd48e56d95f6b33ce729accbd00'
OUT = data.BASE/'PG12902-reply-terminal-trace-v1'
POST = data.BASE/'PG12903-reply-terminal-trace-post-v1'
PROOF = 'b7618d0a1c1e8f15aa08fae490abd8ec584245dd19bfb37288c545026d55a99f'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyCorrelationTerminalRaceTest.java'
MARKER = 'previousReplyTerminalPG12902Reference'

def inputs():
    prior = data.read_checked(data.BASE/'PG12882-pure-health-lifecycle-trace-v1/manifest.json', 'fd37cf51c79ac0962e758ed695ae583e8554052861547e430ed04383ebab8f2a')
    proof = data.read_checked(data.BASE/'PG12900-reply-terminal-post-v1/manifest.json', PROOF)
    normal = data.read_checked(data.BASE/'PG12892-reply-terminal-six-compile-v1/manifest.json', 'f018c19fbaabdc7de2253f8b12a57c86a532177ea40fc9b5448b461aa20ce532')
    assert proof['source'] == normal['source'] == SOURCE and proof['actualExit'] == normal['actualExit'] == 0
    assert proof['observedTestExecutions'] == 9 and proof['selectedTwoMainCoverage100'] and proof['newTestPhysical'] == 1
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,hashes,raw,snap

def reference(prior, proof, hashes, raw):
    value = copy.deepcopy(prior)
    for k in ['actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore']: value.pop(k,None)
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    subjects = ['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'+x+'.java' for x in ['ReplyCorrelationRegistry','PendingReply']]
    assert len(value['sourceRows']) == 983 and all(hashes[r['path']] == r['sha256'] for r in value['sourceRows'])
    assert all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P005-02' for p in subjects)
    assert TEST not in logical and TEST not in {r['path'] for r in value['sourceRows']}
    row = dict(path=TEST,sha256=hashes[TEST],owner='WBS-P005-02',canonicalOwner='WBS-P005-02',canonicalCostOwner='WBS-P005-02',
        changeOwner='WBS-P005-02',basis='2391_SS321_9_TERMINAL_ARBITRATION_CAPACITY_AND_VIEW_INDEPENDENT_ORACLES',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec='evidence/01_PT/018_NK-OPS-001/2391_P005応答終端競合_単体テスト仕様書.md',
        methodTestIds=['PT-JMS-TERM-001','PT-JMS-TERM-002','PT-JMS-TERM-003','PT-JMS-TERM-004'],mainSourceSubjects=subjects,
        ownerProofManifest=str((data.BASE/'PG12900-reply-terminal-post-v1/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF)
    rows = value['sourceRows']+[row]
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe & (set(logical)|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1811 and len(registered) == 1809 and unknown == prior['unregisteredJavaPaths']
    assert len(rows) == len({r['path'] for r in rows}) == 984
    value.update(source=SOURCE,sourceRows=rows,sourceCount=984,registered=1809,javaPaths=1811,registeredMain=965,totalMain=965,
        registeredTest=844,totalTest=846,newPathsAdded=1,newTestPaths=[TEST],
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        currentReplyTerminalBusinessBinding=dict(source=SOURCE,newTest=row,original983AllFieldsPreserved=True,additionalSharedCostPp=0),
        currentReplyTerminalBusinessQualification=dict(source=SOURCE,proofManifestSha256=PROOF,observedTestExecutions=9,newTestIds=4,suites=2,
            selectedTwoMain=proof['selectedTwoMain'],selectedTwoMainCoverage100=True,completeArtifactCounters=proof['completeArtifactCounters'],
            allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1962,newTestPhysical=1,rawStatic=8,staticGateExit=1,spotbugsSixExit=0,
            oldExecUnion=False,newAccepted=0,whole451Accepted=False))
    assert value['newLogicalCandidates'] == prior['newLogicalCandidates']+1
    return value

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name]; assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2392_P005応答終端競合_実行結果.md',currentAddedTestPaths=[TEST])
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1811,registered=1809,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=846,registered=844,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=984,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
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
    assert m['sourceRows'][:-1] == prior['sourceRows'] and m['newAccepted'] == 0
    actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actualraw,actualsnap,json.loads(raw),json.loads(snap))
    assert (actualraw,actualsnap) == documents(raw,snap)
    current = json.loads(actualraw)
    assert all(current[name]['currentAddedTestPaths'] == [TEST] for name in SECTIONS)
    result = audit(); assert result['actualExit'] == 1 and not result['passed']
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),original983AllFieldsPreserved=True,
        newTestCanonicalOwner='WBS-P005-02',newTestCanonicalCostOwner='WBS-P005-02',registered=1809,javaPaths=1811,
        unknownPathsUnchanged=2,wholeWbsAudit=result,whole451Accepted=False,newAccepted=0,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),productTestsExecuted=0))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
