"""Join four-source presentation findings to immutable IDs; no analyzer or product replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11174_current_api_supplied_metric_delta import state as prior_state
from pg11191_api_catalog_scalar_pool_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11200-current-api-catalog-scalar-pool-delta-v1'
SOURCE='5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11174-current-api-supplied-metric-delta-v1/manifest.json','cf033c86870cbc11b4ad8900cc244e2158d82cfaebb6dee0453a34018f4201b4')
    d=data.read_checked(data.BASE/'PG11174-current-api-supplied-metric-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9091,2743,102]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11158-api-metric-fixture-six-compile-v1/manifest.json','580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11191-api-catalog-scalar-pool-context-v1/manifest.json','d661d1e0f7468ba35c20d249153a2af29d58533c3ac211c08e1c81e40d05fd5c')
    rows=data.read_checked(data.BASE/'PG11191-api-catalog-scalar-pool-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11193-api-catalog-scalar-pool-context-post-v1/manifest.json','8d83e5ba41b8ca3396868ae865e289bd6743707574d007f273ea3d070b113559')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='d661d1e0f7468ba35c20d249153a2af29d58533c3ac211c08e1c81e40d05fd5c' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_TAG_COMPARABLE',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==33 and scope<=ids and len(scope&refs)==6 and not scope&pending
    assert len(fresh)==len(fresh_ids)==10 and len(reviewed)==8 and reviewed<fresh_ids
    removed=scope-fresh_ids
    assert len(removed)==23 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9068,2745,110,6323]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=33,newScopeFindings=10,replacedContextWarnings=6,newContextReferencesNet=2,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=9091,
        sourceDerivedRaw=9068,mainRaw=1512,testRaw=7556,totalPriorCorrections=341,sourceScopeCorrectionsAlreadyCounted=23,
        joinedContextWarnings=2745,sourceReboundCurrentWholePending=110,noCurrentReferenceInThisJoin=6323,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
