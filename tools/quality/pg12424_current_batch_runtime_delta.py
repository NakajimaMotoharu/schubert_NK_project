"""Exact five source-derived Test diagnostics removed by actual zero-raw selected analyzer."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12396_current_pool_batch_delta import state as before_batch

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
OUT = data.BASE/'PG12424-current-batch-runtime-delta-v1'

def state():
    ids,refs,pending = before_batch()
    p = data.BASE/'PG12396-current-pool-batch-delta-v1/manifest.json'
    m = data.read_checked(p,'0176966841ad4dfad133672b141c860ddae4edfb278b8d61fd72e76875e95d0a')
    d = data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope = set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    reviewed = {r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids = (ids-set(d['removedFindingIds']))|set(d['addedFindingIds'])
    refs = (refs-scope)|reviewed;pending = (pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)] == [8558,3135,720]
    return ids,refs,pending

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = state()
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    previous = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    changed = {p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p] != h}
    assert list(changed) == ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/bootstrap/BatchRuntimeDependencyTest.java']
    sp = data.BASE/'PG12410-batch-runtime-static-v1';static = data.read_checked(sp/'manifest.json','bb56b5c564bea635bea8d9cd167330f249dc53996b4c7892432bad9e98f43d93')
    assert static['actualExit'] == 0 and static['source'] == SOURCE and static['sourceHashes'] == changed
    for label in ('pmd','checkstyle'):
        raw = (sp/(label+'.xml')).read_bytes();assert data.sha(raw) == static['reports'][label]['sha256']
        assert static['reports'][label]['findings'] == static['reports'][label]['processingErrors'] == 0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    removed = {r['id'] for r in original if r['path'] in changed}
    assert removed == {'PMD-03435','PMD-03436','PMD-03437','PMD-03438','PMD-03439'} and removed <= ids and not removed & (refs|pending)
    assert all(r['rule'] == 'AvoidDuplicateLiterals' and r['inputSha256'] == previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    ids -= removed;assert len(ids) == 8553 and len({r['id'] for r in original}-ids) == 864 and len([i for i in ids if i.startswith('PMD-NEW-')]) == 8
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=5,oldScopeFindings=5,newScopeFindings=0,replacedContextWarnings=0,priorScopePending=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=1,sourceDerivedRaw=8553,mainRaw=1512,testRaw=7041,totalPriorCorrections=864,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=5,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids)-len(refs),actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
