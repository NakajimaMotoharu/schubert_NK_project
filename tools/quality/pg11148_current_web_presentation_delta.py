"""Join four-source presentation findings to immutable IDs; no analyzer or product replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11122_current_web_pure_value_delta import state as prior_state
from pg11139_web_presentation_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11148-current-web-presentation-delta-v1'
SOURCE='497dea5e49082d063d1c41e5e17999a473db6c91'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11122-current-web-pure-value-delta-v1/manifest.json','7964e7e748c4e6d2f2e841ce7666044f399e922579feb8f2bd339837a1c4977d')
    d=data.read_checked(data.BASE/'PG11122-current-web-pure-value-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9143,2738,85]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11106-web-pure-value-six-compile-v1/manifest.json','77fd485d4718416d3cb75e57e16458d2633289b432bb30a97738d326edcc364b')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==4 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11139-web-presentation-context-v1/manifest.json','b625b3a26cbe109f4b5ddfddc58fa3b4e2a0461e78f0d87efba670552e24c0c0')
    rows=data.read_checked(data.BASE/'PG11139-web-presentation-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11141-web-presentation-context-post-v1/manifest.json','0c7d9cff1b0bc6c376573f4a5e4d176edf2b11ce7f14d2ca3278db84769cf797')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='b625b3a26cbe109f4b5ddfddc58fa3b4e2a0461e78f0d87efba670552e24c0c0',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==14 and scope<=ids and len(scope&refs)==4 and not scope&pending
    assert len(fresh)==len(fresh_ids)==len(reviewed)==5 and fresh_ids==reviewed
    removed=scope-fresh_ids
    assert len(removed)==9 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9134,2739,90,6395]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=14,newScopeFindings=5,replacedContextWarnings=4,newContextReferencesNet=1,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=9143,
        sourceDerivedRaw=9134,mainRaw=1512,testRaw=7622,totalPriorCorrections=275,sourceScopeCorrectionsAlreadyCounted=9,
        joinedContextWarnings=2739,sourceReboundCurrentWholePending=90,noCurrentReferenceInThisJoin=6395,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
