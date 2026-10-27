"""Join one HTTP recorder fixture finding scope and6 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11254_current_batch_metric_label_delta import state as prior_state
from pg11271_http_recorder_fixture_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11280-current-http-recorder-delta-v1'
SOURCE='064294de0f47e195a99e5fab76e2fe92ea31256d'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11254-current-batch-metric-label-delta-v1/manifest.json','ececd6a74d48472d2ababb2cbb83c8239b023299b1c5f98067cbd4002178a6c2')
    d=data.read_checked(data.BASE/'PG11254-current-batch-metric-label-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9010,2753,132]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1/manifest.json','5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11271-http-recorder-fixture-context-v1/manifest.json','3794a7f23d8a923c689dc7c7e50e299bca308559c9f9dd3682b68bac39e204db')
    rows=data.read_checked(data.BASE/'PG11271-http-recorder-fixture-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11273-http-recorder-fixture-context-post-v1/manifest.json','6056bcc746860f557acac91224ccd1b5953a127941d986993143658f28a53a9c')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='3794a7f23d8a923c689dc7c7e50e299bca308559c9f9dd3682b68bac39e204db' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==16 and scope<=ids and len(scope&refs)==5 and not scope&pending
    assert len(fresh)==len(fresh_ids)==6 and len(reviewed)==6 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==10 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidFieldNameMatchingMethodName','CloseResource') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9000,2754,138,6246]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=16,newScopeFindings=6,replacedContextWarnings=5,newContextReferencesNet=1,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=9010,
        sourceDerivedRaw=9000,mainRaw=1512,testRaw=7488,totalPriorCorrections=409,sourceScopeCorrectionsAlreadyCounted=10,
        joinedContextWarnings=2754,sourceReboundCurrentWholePending=138,noCurrentReferenceInThisJoin=6246,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
