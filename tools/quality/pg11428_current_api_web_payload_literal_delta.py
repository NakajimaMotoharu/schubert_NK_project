"""Join current payload literal32to24; retain four previous CloseResource fixes to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11396_current_full_payload_guard_delta import state as prior_state
from pg11419_api_web_payload_literal_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11428-current-api-web-payload-literal-delta-v1'
SOURCE='2d733dbd80350c819b732ae3d9b9b0f85ba0172f'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11396-current-full-payload-guard-delta-v1/manifest.json','63c79243e29df631ae65e6a73b1a0e742b509cfaff1b10a812a2c84eb6fdc5ca')
    d=data.read_checked(data.BASE/'PG11396-current-full-payload-guard-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[8920,2757,194]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11380-full-payload-guard-six-compile-v1/manifest.json','f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11419-api-web-payload-literal-context-v1/manifest.json','e964c90a01aabb69a408b5a233007e0789e5e4c07cfa8d4b214c15d5c0f4f55c')
    rows=data.read_checked(data.BASE/'PG11419-api-web-payload-literal-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11421-api-web-payload-literal-context-post-v1/manifest.json','a306fbe009e3ea469fd989820459052e9c5f2e314a05866a2ce44585a546fd45')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='e964c90a01aabb69a408b5a233007e0789e5e4c07cfa8d4b214c15d5c0f4f55c' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    scope=original_scope&ids
    assert len(original_scope)==36 and len(scope)==32 and len(scope&refs)==24 and len(scope&pending)==24
    assert all(r['rule']=='CloseResource' for r in original if r['id'] in original_scope-scope)
    assert len(fresh)==len(fresh_ids)==24 and len(reviewed)==24 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==8 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[8912,2757,194,6155]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        originalScopeFindings=36,previouslyRemovedIds=sorted(original_scope-scope),oldScopeFindings=32,newScopeFindings=24,replacedContextWarnings=24,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8920,
        sourceDerivedRaw=8912,mainRaw=1512,testRaw=7400,totalPriorCorrections=497,sourceScopeCorrectionsAlreadyCounted=8,
        joinedContextWarnings=2757,sourceReboundCurrentWholePending=194,noCurrentReferenceInThisJoin=6155,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
