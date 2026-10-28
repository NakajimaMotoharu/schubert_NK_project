"""Actual nine thread-context rows and exact one naming correction; retain raw gate and erratum."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12904_reply_terminal_context import state_after as previous_state

SOURCE = '4a3fad244f21530547fdc79b16f9ea3af0ca13af'
OUT = data.BASE/'PG12928-coordinator-context-v1'
POST = data.BASE/'PG12929-coordinator-context-post-v1'
REMOVED = {'PMD-08077'}

def state_after():
    ids,refs,pending = previous_state()
    current = {'PMD-07356', 'PMD-08111', 'PMD-08112'}|{'PMD-'+str(i).zfill(5) for i in range(8071,8077)}
    assert REMOVED <= ids and not REMOVED & (refs|pending) and current <= refs and len(current) == 9
    return ids-REMOVED,refs,pending|current

def expected():
    static = data.read_checked(data.BASE/'PG12924-coordinator-corrected-static-v1/manifest.json','6b939db5f3785efd4296d055692e0a3f038069924ed07c31abd8524b70b2f694')
    proof = data.read_checked(data.BASE/'PG12926-coordinator-corrected-post-v1/manifest.json','b3904e8e05c97c403ff65e65793dae5d3e447c564c61cbd7150262e7041ea3f9')
    normal = data.read_checked(data.BASE/'PG12920-coordinator-corrected-six-compile-v1/manifest.json','14e6f1dce556fe58dc1ecdea73c0b65ab6dbc45d82625601eae1732378e239cc')
    assert static['source'] == proof['source'] == normal['source'] == SOURCE
    assert static['actualExit'] == 1 and proof['actualExit'] == normal['actualExit'] == 0
    assert proof['observedTestExecutions'] == 17 and proof['selectedFiveMainCoverage100']
    assert proof['rawStatic'] == len(proof['rawFindings']) == 9 and proof['rawRuleCounts'] == {'DoNotUseThreads':9}
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in normal['begin']['inputHashes'].items())
    ids_by_name = {'JmsRequestReplyClient.java':['PMD-07356'], 'JmsRequestReplyClientTest.java':['PMD-'+str(i).zfill(5) for i in range(8071,8077)], 'ReplyCorrelationRegistryTest.java':['PMD-08111','PMD-08112']}
    p = data.BASE/'PG12924-coordinator-corrected-static-v1/pmd.xml'
    assert data.sha(p.read_bytes()) == static['reports']['pmd']['sha256']
    result = []
    for f in ET.parse(p).getroot():
        if f.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(f.get('name')).relative_to(data.ROOT)); text = (data.ROOT/path).read_text(); name = Path(path).name
        assert name in ids_by_name and len(list(f)) == len(ids_by_name[name])
        assert data.sha(text.encode()) == static['sourceHashes'][path]
        for identifier,node in zip(ids_by_name[name],f):
            assert node.get('rule') == 'DoNotUseThreads'
            line = int(node.get('beginline')); end = int(node.get('endline'))
            if name == 'JmsRequestReplyClient.java':
                method = 'exchange'; reason = 'Required InterruptedException branch cancels own pending, restores current caller interrupt flag, rethrows classified failure, finally releases own wait permit; does not start another thread'
                assert 'Thread.currentThread().interrupt();' in '\n'.join(text.splitlines()[line-1:end])
            else:
                prefix = '\n'.join(text.splitlines()[:line])
                methods = re.findall(r'(?:@Test\s+void|private static void)\s+(\w+)\s*\(',prefix)
                assert methods; method = methods[-1]
                reason = 'Self-owned interrupted waiter joined2s with finally interrupt/join, or configured1/12/20 workers and release-finally with future.get2s; helper restores own interrupt; Registry16workers100calls get5s/TWR'
            result.append(dict(id=identifier,path=path,sha256=static['sourceHashes'][path],rule=node.get('rule'),beginline=line,endline=end,
                enclosingMethod=method,source=SOURCE,canonicalOwner='WBS-P005-02',canonicalCostOwner='WBS-P005-02',reason=reason,
                limitation='TWR close/latch helper itself locally unbounded; finally release on failures and dedicated outer JVM240s retained',
                classification='EXPLICIT_INTERRUPT_CONTRACT_OR_FINITE_SELF_OWNED_TEST_WORKER_CONTEXT',actualGateExit=1,actualViolation=None))
    assert len(result) == len({r['id'] for r in result}) == 9
    assert not any('/JmsRequestReplyCleanupTest.java' in r['path'] for r in result)
    oldstatic = data.read_checked(data.BASE/'PG12914-coordinator-static-v1/manifest.json','032eab4fc9aecc313a5412621821f5942b1d05ea9137d95fecd2aac653034ece')
    oldpost = data.read_checked(data.BASE/'PG12916-coordinator-post-v1/manifest.json','302c87f33df40c5204561c1e58e556e04768f1b78ff34950825927cd4f2ede21')
    oldxml = data.BASE/'PG12914-coordinator-static-v1/pmd.xml'
    assert data.sha(oldxml.read_bytes()) == oldstatic['reports']['pmd']['sha256']
    oldrows = [r for r in ET.parse(oldxml).getroot().iter() if r.tag.rpartition('}')[2] == 'violation']
    assert len(oldrows) == 10 and oldpost['rawStatic'] == 8 and static['toolAndRuleHashes'] == oldstatic['toolAndRuleHashes']
    ids,refs,pending = state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8472,3200,881,5272]
    return dict(source=SOURCE,rows=result,sourceDerivedRaw=8472,mainRaw=1505,testRaw=6967,totalPriorCorrections=951,
        removedFindingIds=sorted(REMOVED),addedFindingIds=[],introducedFindingsRetained=14,joinedContextWarnings=3200,
        sourceReboundCurrentWholePending=881,noCurrentReferenceInThisJoin=5272,newContextClassifications=0,newSourceRebindings=9,
        scopeRaw=9,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,
        formerPostErratum=dict(source=oldpost['source'],manifestSha256='302c87f33df40c5204561c1e58e556e04768f1b78ff34950825927cd4f2ede21',
            originalRawStaticCaption=8,actualXmlRaw=10,actualPmdXmlSha256=data.sha(oldxml.read_bytes()),originalEntryAndManifestPreserved=True,
            oldCaptionNotUsableForAcceptanceOrRawTotals=True,oldCoverageAndXmlNotReplayed=True),
        rawCountsDerivation='previous8473 minus original PMD08077 field/method name; new Cleanup Test has zero raw, other old source and allMain unchanged',
        expectedIndependentTests=17,newBusinessTestIds=4,newAccepted=0,wholeF03Accepted=False,oldExecUnion=False,externalActions=0)

def main():
    invocation = capture(__file__); assert not OUT.exists(); value = expected(); verify(invocation); OUT.mkdir()
    data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        sourceDerivedRaw=8472,totalPriorCorrections=951,rawScope=9,removedFindingIds=sorted(REMOVED),actualViolationCount=None,
        wholeF03Accepted=False,newAccepted=0,productTestsExecuted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__); assert not POST.exists()
    m = json.loads((OUT/'manifest.json').read_bytes()); value = data.read_checked(OUT/'review.json',m['reviewSha256'])
    reference = expected(); assert m['actualExit'] == 0 and value == reference
    labels = []
    for k,v in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',950),('scopeRaw',8),('newAccepted',1),('wholeF03Accepted',True),('actualViolationCount',0),('removedFindingIds',[]),('addedFindingIds',['forged'])]:
        bad = copy.deepcopy(value); assert bad[k] != v; bad[k] = v; assert bad != reference; labels.append(k)
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceDerivedRaw=8472,actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
