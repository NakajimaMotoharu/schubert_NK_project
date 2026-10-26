"""Reconcile already-corrected original 28 Inbox Test warnings; zero analyzer or test replay."""
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state

OUT=data.BASE/'PG11096-current-inbox-value-delta-v1'
SOURCE='f97723798f3f71a9112b4bbecfba531dba9b34b6'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    parent=data.read_checked(data.BASE/'PG11058-current-api-request-delta-v1/manifest.json','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390')
    delta=data.read_checked(data.BASE/'PG11058-current-api-request-delta-v1/delta.json',parent['deltaSha256'])
    parent_post=data.read_checked(data.BASE/'PG11060-current-api-request-delta-post-v1/manifest.json','7ec7bdff13c480d1cc122c22f594e4bc60349b5b71e7250e82f0b26159dbba82')
    assert parent_post['actualExit']==0 and parent_post['source']==parent['source']
    ids,refs,pending=state()
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids-=set(delta['removedFindingIds'])
    refs=(refs-scope)|reviewed
    pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[9190,2737,76]
    normal=data.read_checked(data.BASE/'PG11080-inbox-lifecycle-six-compile-v1/manifest.json','a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641')
    previous=data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert len(current)==1810 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in current.items())
    changed={p:h for p,h in current.items() if previous['begin']['inputHashes'][p]!=h}
    static_path=data.BASE/'PG11084-inbox-lifecycle-static-v1/manifest.json'
    static=data.read_checked(static_path,'d7aaaad5997bd39faeb386dcdfbc5c605c8f42cdf5c51f6eea9fe7423d6a8404')
    assert static['actualExit']==0 and static['source']==normal['source']==SOURCE and changed==static['sourceHashes'] and len(changed)==4
    assert all(r['findings']==r['processingErrors']==0 for r in static['reports'].values())
    for name,r in static['reports'].items():
        assert data.sha((static_path.parent/(name+'.xml')).read_bytes())==r['sha256']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    gone=[r for r in original if r['path'] in changed]
    removed={r['id'] for r in gone}
    assert len(removed)==28 and removed<=ids and not removed&refs and not removed&pending
    assert Counter(r['rule'] for r in gone)==Counter(AvoidDuplicateLiterals=12,CloseResource=15,AvoidLiteralsInIfCondition=1)
    assert [len(ids-removed),len(refs),len(pending),len((ids-removed)-refs)]==[9162,2737,76,6425]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,removedFindingIds=sorted(removed),freshRows=[],
        oldScopeFindings=28,newScopeFindings=0,ruleCorrections=dict(AvoidDuplicateLiterals=12,CloseResource=15,AvoidLiteralsInIfCondition=1)))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        parentManifestSha256='369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390',deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=9190,
        sourceDerivedRaw=9162,mainRaw=1512,testRaw=7650,totalPriorCorrections=247,sourceScopeCorrectionsAlreadyCounted=28,
        joinedContextWarnings=2737,sourceReboundCurrentWholePending=76,noCurrentReferenceInThisJoin=6425,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
