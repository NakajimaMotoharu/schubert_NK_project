"""Six explicit worker/oracle contexts; add two new raw findings, not candidate-style corrections."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12928_coordinator_context import state_after as previous_state

SOURCE = 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
OUT = data.BASE/'PG12964-public-receipt-context-v1'
POST = data.BASE/'PG12965-public-receipt-context-post-v1'
NEW = {'PMD-NEW-RECEIPT-001','PMD-NEW-RECEIPT-002'}
CURRENT = {'PMD-00617','PMD-00618','PMD-00619','PMD-00620'}|NEW

def state_after():
    ids,refs,pending = previous_state()
    assert not NEW & (ids|refs|pending)
    assert CURRENT-NEW <= ids and (CURRENT-NEW)&refs == {'PMD-00619'} and not CURRENT&pending
    return ids|NEW,refs|CURRENT,pending|CURRENT

def expected():
    static = data.read_checked(data.BASE/'PG12960-public-receipt-static-v1/manifest.json','052425b356a762c807453874a1c2fcd87b9b8997ea0a5d0fec23de7eee909d9b')
    proof = data.read_checked(data.BASE/'PG12962-public-receipt-post-v1/manifest.json','32352ff9472707da5adfcbec67cadd5783a053e61dfce843217da5921e303f99')
    assert static['source'] == proof['source'] == SOURCE and static['actualExit'] == 1 and proof['actualExit'] == 0
    assert proof['selectedTwoMainCoverage100'] and proof['observedTestExecutions'] == 12 and proof['rawStatic'] == len(proof['rawFindings']) == 6
    assert proof['rawRuleCounts'] == {'DoNotUseThreads':3,'UseConcurrentHashMap':2,'AvoidSynchronizedStatement':1}
    p = data.BASE/'PG12960-public-receipt-static-v1/pmd.xml'
    assert data.sha(p.read_bytes()) == static['reports']['pmd']['sha256']
    rows = []
    for f in ET.parse(p).getroot():
        if f.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(f.get('name')).relative_to(data.ROOT)); text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == static['sourceHashes'][path]
        original = path.endswith('/QuestionReceiptIdTest.java')
        assert original or path.endswith('/QuestionReceiptRecoveryTest.java')
        identifiers = ['PMD-00617','PMD-00618','PMD-00619','PMD-00620'] if original else sorted(NEW)
        assert len(list(f)) == len(identifiers)
        for identifier,node in zip(identifiers,f):
            line = int(node.get('beginline')); end = int(node.get('endline')); rule = node.get('rule')
            methods = re.findall(r'(?:@Test\s+(?:@DisplayName\([^\n]+\)\s+)?void|private static QuestionReceiptId)\s+(\w+)\s*\(', '\n'.join(text.splitlines()[:line]))
            assert methods; method = methods[-1]
            if original:
                assert method == 'concurrentCalls'
                reason = {'UseConcurrentHashMap':'Independent literal histogram and actual histogram updated only by caller after future.get; workers return values, no map capture/mutation',
                    'DoNotUseThreads':'Self-owned8workers/64 tasks, each future.get5s, TWR',
                    'AvoidSynchronizedStatement':'Intentional public monitor held by caller to prove generator private ReentrantLock is independent; retain oracle, not Production synchronized'}[rule]
            else:
                assert rule == 'DoNotUseThreads' and method == 'fromAnotherThread'
                reason = 'Self-owned single worker checks lock ownership transfer after provider failure; future.get5s/TWR, memory callback only'
            rows.append(dict(id=identifier,path=path,sha256=static['sourceHashes'][path],rule=rule,beginline=line,endline=end,
                enclosingMethod=method,source=SOURCE,canonicalOwner='WBS-P011-01',canonicalCostOwner='WBS-P011-01',reason=reason,
                limitation='TWR close and ReentrantLock.lock locally unbounded; separate JVM240s preserves run deadline',actualGateExit=1,actualViolation=None))
    assert len(rows) == len({r['id'] for r in rows}) == 6 and {r['id'] for r in rows} == CURRENT
    ids,refs,pending = state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8474,3205,887,5269]
    return dict(source=SOURCE,rows=rows,sourceDerivedRaw=8474,mainRaw=1505,testRaw=6969,totalPriorCorrections=951,
        introducedFindingsRetained=16,newContextClassifications=5,existingSourceRebindings=1,
        joinedContextWarnings=3205,sourceReboundCurrentWholePending=887,noCurrentReferenceInThisJoin=5269,
        addedFindingIds=sorted(NEW),removedFindingIds=[],globalPriorSourceCorrectionsAdded=0,
        candidateAuthoringStyleCorrections=2,scopeRaw=6,staticActualExit=1,actualViolationCount=None,
        ownedPublicTrace=proof['ownedPublicTrace'],ownedCwdTraceOnlyNotHostWideFsAudit=True,
        rawCountsDerivation='Previous8472 plus new Test two Thread findings; original source/Main/Test unchanged; pre-freeze magic13/25 were not baseline findings',
        wholeCurrentAnalyzerReissued=False,newAccepted=0,wholeF03Accepted=False,oldExecUnion=False,productTestsExecuted=0)

def main():
    invocation = capture(__file__); assert not OUT.exists(); value = expected(); verify(invocation); OUT.mkdir()
    data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        sourceDerivedRaw=8474,totalPriorCorrections=951,rawScope=6,newFindingIds=sorted(NEW),actualViolationCount=None,
        sourceReboundCurrentWholePending=887,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__); assert not POST.exists()
    m = json.loads((OUT/'manifest.json').read_bytes()); value = data.read_checked(OUT/'review.json',m['reviewSha256']); reference = expected()
    assert m['actualExit'] == 0 and value == reference; labels = []
    for k,v in [('source','0'*40),('sourceDerivedRaw',8472),('totalPriorCorrections',953),('scopeRaw',0),('globalPriorSourceCorrectionsAdded',2),('addedFindingIds',[]),('actualViolationCount',0),('newAccepted',1),('wholeF03Accepted',True)]:
        bad = copy.deepcopy(value); assert bad[k] != v; bad[k] = v; assert bad != reference; labels.append(k)
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceDerivedRaw=8474,totalPriorCorrections=951,
        actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
