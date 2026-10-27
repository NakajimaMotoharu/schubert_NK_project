"""Join six Batch standard-to-text fixture finding scopes and20 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11280_current_http_recorder_delta import state as prior_state
from pg11297_batch_standard_text_fixture_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11306-current-batch-standard-text-delta-v1'
SOURCE='d431ad964355c4e5c602fcb94fe0182da6ae3a61'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11280-current-http-recorder-delta-v1/manifest.json','c7e3191fd0c829b2010adc6ec6ab2f88f0516198358b539bbf1d9e206fef72e3')
    d=data.read_checked(data.BASE/'PG11280-current-http-recorder-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9000,2754,138]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11264-http-recorder-fixture-six-compile-v1/manifest.json','87b29c22a2f3b612936173d8633cd67201368bc1f711938a0f1e834624f17d9f')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==6 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11297-batch-standard-text-fixture-context-v1/manifest.json','0bc9214c567afda1d18ad4441b016c7ec780f59ec7ef31f5d118d015cf8f4be4')
    rows=data.read_checked(data.BASE/'PG11297-batch-standard-text-fixture-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11299-batch-standard-text-fixture-context-post-v1/manifest.json','f86c7f68cc9d8f0fa2d8c2772d6772bcd521c7e1869a35d439156d66e8dd2c86')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='0bc9214c567afda1d18ad4441b016c7ec780f59ec7ef31f5d118d015cf8f4be4' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==79 and scope<=ids and len(scope&refs)==19 and not scope&pending
    assert len(fresh)==len(fresh_ids)==52 and len(reviewed)==20 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==27 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[8973,2755,158,6218]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=79,newScopeFindings=52,replacedContextWarnings=19,newContextReferencesNet=1,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=6,otherSourcePathsUnchanged=1804,originalRaw=9409,priorDerivedRaw=9000,
        sourceDerivedRaw=8973,mainRaw=1512,testRaw=7461,totalPriorCorrections=436,sourceScopeCorrectionsAlreadyCounted=27,
        joinedContextWarnings=2755,sourceReboundCurrentWholePending=158,noCurrentReferenceInThisJoin=6218,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
