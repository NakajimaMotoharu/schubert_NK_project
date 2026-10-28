"""Two original real corrections, four retained self-worker raw rows, no global zero inference."""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12964_public_receipt_context import state_after as previous_state

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
OUT = data.BASE/'PG13026-http-route-name-context-v1'
POST = data.BASE/'PG13027-http-route-name-context-post-v1'
REMOVED = {'PMD-07371','PMD-08207'}
CURRENT = {'PMD-08208','PMD-08209','PMD-08210','PMD-08211'}

def state_after():
    ids,refs,pending = previous_state()
    assert REMOVED <= ids & refs & pending and CURRENT <= ids & refs & pending
    return ids-REMOVED,refs-REMOVED,pending-REMOVED

def expected():
    s = data.read_checked(data.BASE/'PG13022-http-route-name-static-v1/manifest.json','c4e96da7639188621b5e4477fca68d6bd10d17e09c7a6bdce23ca375249bf21c')
    p = data.read_checked(data.BASE/'PG13024-http-route-name-post-v1/manifest.json','6d4088dfc5b7b254ef4aaa652c41a3dd0e49d0106a0cfdc7759c5d1cffe19a1c')
    assert s['source'] == p['source'] == SOURCE and s['actualExit'] == 1 and p['actualExit'] == 0
    assert p['observedTestExecutions'] == 6 and p['selectedMainCoverage100'] and len(p['selectedMain']) == 6
    assert p['rawStatic'] == len(p['rawFindings']) == 4 and p['rawRuleCounts'] == {'DoNotUseThreads':4}
    assert p['mainChangedPhysical'] == 5 and p['allOtherMainClassesUnchanged'] == 1838 and p['oldTestPhysicalUnchanged'] == 1969 and p['changedTestPhysical'] == 1
    path = data.BASE/'PG13022-http-route-name-static-v1/pmd.xml'
    assert data.sha(path.read_bytes()) == s['reports']['pmd']['sha256']
    reasons = ['Self-owned4worker test executor, not production container work','Fixed64tasks/invokeAll10seconds, caller get of each terminal future','Original finally shutdownNow of that same executor','Original awaitTermination10seconds plus outer TWR; outer dedicated JVM240s bound retained']
    rows = []
    for f in ET.parse(path).getroot():
        if f.tag.rpartition('}')[2] != 'file': continue
        source = str(Path(f.get('name')).relative_to(data.ROOT))
        assert source.endswith('/HttpMetricContractTest.java') and len(list(f)) == 4
        assert data.sha((data.ROOT/source).read_bytes()) == s['sourceHashes'][source]
        for identifier,node,reason in zip(sorted(CURRENT),f,reasons):
            assert node.get('rule') == 'DoNotUseThreads' and node.get('method') == 'httpMetric006ConcurrentClassifiersAreStateless'
            rows.append(dict(id=identifier,path=source,source=SOURCE,sha256=s['sourceHashes'][source],rule=node.get('rule'),beginline=int(node.get('beginline')),endline=int(node.get('endline')),
                enclosingMethod=node.get('method'),canonicalOwner='WBS-P018-09',canonicalCostOwner='WBS-P018-09',reason=reason,
                classification='FINITE_SELF_OWNED_TEST_WORKER_RAW_RETAINED_PENDING_WHOLE_F03',actualGateExit=1,actualViolation=None,
                limitation='TWR close locally unbounded if await/assert fails; outer JVM deadline preserved, actual owned whole6 run terminal0'))
    ids,refs,pending = state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8472,3203,885,5269]
    return dict(source=SOURCE,rows=rows,sourceDerivedRaw=8472,mainRaw=1504,testRaw=6968,totalPriorCorrections=953,
        removedFindingIds=sorted(REMOVED),addedFindingIds=[],introducedFindingsRetained=16,globalBaselineCorrectionsAdded=2,
        mainCorrections=1,testCorrections=1,newContextClassifications=0,existingSourceRebindings=4,
        joinedContextWarnings=3203,sourceReboundCurrentWholePending=885,noCurrentReferenceInThisJoin=5269,
        rawScope=4,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,
        scopeSixMainCoverage100=True,mainPhysicalDiff=p['mainSourceMetadata'],rawCodeCpIndicesNotSemanticProof=True,
        proofOfSameBehavior='Exact original1157Main/1971Test token inverse+six negative vectors and actual whole6/golden35 resource; raw Code bytes alone are not semantics',
        expectedIndependentTests=6,newTestIds=0,newAccepted=0,wholeF03Accepted=False,oldExecUnion=False,externalActions=0)

def main():
    invocation = capture(__file__); assert not OUT.exists(); value = expected(); verify(invocation); OUT.mkdir()
    data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        sourceDerivedRaw=8472,totalPriorCorrections=953,rawScope=4,removedFindingIds=sorted(REMOVED),actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__); assert not POST.exists()
    m = json.loads((OUT/'manifest.json').read_bytes()); value = data.read_checked(OUT/'review.json',m['reviewSha256']); reference = expected()
    assert m['actualExit'] == 0 and value == reference; labels = []
    for key,bad_value in [('source','0'*40),('sourceDerivedRaw',8474),('totalPriorCorrections',951),('removedFindingIds',[]),('rawScope',0),('actualViolationCount',0),('globalBaselineCorrectionsAdded',0),('newAccepted',1),('wholeF03Accepted',True)]:
        bad = copy.deepcopy(value); assert bad[key] != bad_value; bad[key] = bad_value; assert bad != reference; labels.append(key)
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceDerivedRaw=8472,totalPriorCorrections=953,actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
