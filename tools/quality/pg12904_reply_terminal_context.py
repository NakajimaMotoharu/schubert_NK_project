"""Source-bound finite worker contexts; add six actual new raw findings, never suppress them."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12884_current_pure_health_lifecycle_delta import state_after as before_state

SOURCE = '5590eee0d766fdd48e56d95f6b33ce729accbd00'
OUT = data.BASE/'PG12904-reply-terminal-context-v1'
POST = data.BASE/'PG12905-reply-terminal-context-post-v1'
NEW = {'PMD-NEW-REPLYTERM-'+str(i).zfill(3) for i in range(1,7)}

def rows():
    s = data.read_checked(data.BASE/'PG12898-reply-terminal-static-v1/manifest.json','1b6116f3dd3e95f3b75dca863c4055be4562cb4fa10fa6e142ac91d72535b64f')
    p = data.BASE/'PG12898-reply-terminal-static-v1/pmd.xml'
    assert data.sha(p.read_bytes()) == s['reports']['pmd']['sha256']
    assert s['source'] == SOURCE and s['actualExit'] == 1 and s['spotbugsSixExit'] == 0
    result = []; new_index = 0
    for file in ET.parse(p).getroot():
        if file.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT)); text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == s['sourceHashes'][path]
        old = path.endswith('/ReplyCorrelationRegistryTest.java')
        assert old or path.endswith('/ReplyCorrelationTerminalRaceTest.java')
        for index,node in enumerate(file):
            assert node.get('rule') == 'DoNotUseThreads'
            line = int(node.get('beginline')); end = int(node.get('endline'))
            prefix = '\n'.join(text.splitlines()[:line])
            names = re.findall(r'@Test\s+void\s+(\w+)\s*\(',prefix); assert names
            method = names[-1]
            if old:
                assert method == 'oneOfOneHundredSimultaneousResponsesWins'
                identifier = ['PMD-08111','PMD-08112'][index]
                reason = 'Self-owned16 workers/100 tasks, release latch before future.get5s, TWR; no external broker or process'
            else:
                new_index += 1; identifier = 'PMD-NEW-REPLYTERM-'+str(new_index).zfill(3)
                assert method in ['terminalRaceHasOneWinnerAndReturnsThePermit','concurrentRegistrationsRespectCapacityAndReuseAllSlots']
                reason = 'Self-owned3 workers/64 rounds/three terminal calls, or20 workers/20 distinct IDs; latch finally releases; each future.get10s, TWR'
            result.append(dict(id=identifier,path=path,sha256=s['sourceHashes'][path],rule=node.get('rule'),beginline=line,endline=end,
                enclosingMethod=method,source=SOURCE,reason=reason,
                limitation='TWR close and in-memory future completion itself have no local deadline; dedicated outer JVM240s bounds the run',
                expectedOracle='Exactly one terminal owner/capacity1 or exactly two accepted/eighteen rejected; independent literals2391',
                actualGateExit=1,classification='FINITE_TEST_WORKER_CONTEXT_NOT_RULE_SUPPRESSION',actualViolation=None))
    assert len(result) == 8 and new_index == 6 and {r['id'] for r in result} == NEW|{'PMD-08111','PMD-08112'}
    return result

def state_after():
    ids,refs,pending = before_state()
    assert not NEW & (ids|refs|pending)
    return ids|NEW,refs|NEW,pending|NEW|{'PMD-08111','PMD-08112'}

def expected():
    r = rows()
    proof = data.read_checked(data.BASE/'PG12900-reply-terminal-post-v1/manifest.json','b7618d0a1c1e8f15aa08fae490abd8ec584245dd19bfb37288c545026d55a99f')
    assert proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['selectedTwoMainCoverage100']
    assert proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1962 and proof['newTestPhysical'] == 1
    ids,refs,pending = state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8473,3200,874,5273]
    return dict(source=SOURCE,rows=r,sourceDerivedRaw=8473,mainRaw=1505,testRaw=6968,totalPriorCorrections=950,
        introducedFindingsRetained=14,joinedContextWarnings=3200,sourceReboundCurrentWholePending=874,noCurrentReferenceInThisJoin=5273,
        addedFindingIds=sorted(NEW),removedFindingIds=[],newContextClassifications=6,existingSourceRebindings=2,
        scopeRaw=8,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,
        rawCountsDerivation='previous8467 plus new Test six; all original source and all1843Main/1962Test bytes unchanged, same static tools/rules',
        expectedIndependentTests=9,newBusinessTestIds=4,newAccepted=0,wholeF03Accepted=False,oldExecUnion=False,externalActions=0)

def main():
    invocation = capture(__file__); assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG12874-pure-health-lifecycle-static-v1/manifest.json','2369a8378b3be015e6ab03f034cbe38d4d4feb9d31797aa2119d13551fa2e90e')
    current = data.read_checked(data.BASE/'PG12898-reply-terminal-static-v1/manifest.json','1b6116f3dd3e95f3b75dca863c4055be4562cb4fa10fa6e142ac91d72535b64f')
    assert old['toolAndRuleHashes'] == current['toolAndRuleHashes']
    value = expected(); verify(invocation); OUT.mkdir(); data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        sourceDerivedRaw=8473,rawScope=8,newFindingIds=sorted(NEW),removedFindingIds=[],newAccepted=0,wholeF03Accepted=False,
        actualViolationCount=None,sourceReboundCurrentWholePending=874,productTestsExecuted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__); assert not POST.exists()
    m = json.loads((OUT/'manifest.json').read_bytes()); value = data.read_checked(OUT/'review.json',m['reviewSha256'])
    assert m['actualExit'] == 0 and value == expected()
    labels = []
    for field,bad_value in [('source','0'*40),('scopeRaw',0),('sourceDerivedRaw',8467),('mainRaw',0),('testRaw',0),('newContextClassifications',0),('newAccepted',1),('wholeF03Accepted',True),('addedFindingIds',[]),('actualViolationCount',0),('staticActualExit',0)]:
        bad = copy.deepcopy(value); assert bad[field] != bad_value; bad[field] = bad_value
        assert bad != expected(); labels.append(field)
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceDerivedRaw=8473,actualViolationCount=None,wholeF03Accepted=False,newAccepted=0))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
