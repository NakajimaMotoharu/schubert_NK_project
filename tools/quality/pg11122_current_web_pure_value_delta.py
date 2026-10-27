"""Current three-source Web literal delta and nine contexts; never replay target tests/analyzers."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state as previous_state
from pg11113_web_pure_value_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11122-current-web-pure-value-delta-v1'
SOURCE='5fce2af667d8d5cdd9b67da9b02080b105848c28'


def state():
    ids,refs,pending=previous_state()
    m=data.read_checked(data.BASE/'PG11058-current-api-request-delta-v1/manifest.json','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390')
    d=data.read_checked(data.BASE/'PG11058-current-api-request-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    fresh={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|fresh
    pending=(pending-scope)|fresh
    m=data.read_checked(data.BASE/'PG11096-current-inbox-value-delta-v1/manifest.json','1c3f95f4b7cb74ea442043405db8d089997e8fa7ed88986fff270aa74a67d2a1')
    d=data.read_checked(data.BASE/'PG11096-current-inbox-value-delta-v1/delta.json',m['deltaSha256'])
    assert not set(d['removedFindingIds'])&refs and not set(d['removedFindingIds'])&pending
    ids-=set(d['removedFindingIds'])
    assert [len(ids),len(refs),len(pending)]==[9162,2737,76]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11080-inbox-lifecycle-six-compile-v1/manifest.json','a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert len(current)==1810
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(changed)==3 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11113-web-pure-value-context-v1/manifest.json','33b0641d03cfa5bf59029068e376ad180cbf2e1c228d4550741b2cf898b05d0c')
    reviewed_rows=data.read_checked(data.BASE/'PG11113-web-pure-value-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11115-web-pure-value-context-post-v1/manifest.json','8981f66ee5dfc0c865f2192d6db23bedee0c7c9435ebca5fef6e08df170a68b1')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in reviewed_rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],
            contextManifestSha256='33b0641d03cfa5bf59029068e376ad180cbf2e1c228d4550741b2cf898b05d0c' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_MUTABLE_TAG_COMPARABLE',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==29 and scope<=ids and len(scope&refs)==8 and not scope&pending
    assert len(fresh)==len(fresh_ids)==10 and len(reviewed)==9 and reviewed<=fresh_ids
    removed=scope-fresh_ids
    assert len(removed)==19 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9143,2738,85,6405]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=29,newScopeFindings=10,replacedContextWarnings=8,newContextReferencesNet=1,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=9162,
        sourceDerivedRaw=9143,mainRaw=1512,testRaw=7631,totalPriorCorrections=266,sourceScopeCorrectionsAlreadyCounted=19,
        joinedContextWarnings=2738,sourceReboundCurrentWholePending=85,noCurrentReferenceInThisJoin=6405,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
