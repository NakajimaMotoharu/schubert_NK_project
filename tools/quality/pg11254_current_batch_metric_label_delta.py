"""Join three supplied Batch metric label fixture findings and8 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11228_current_web_supplied_metric_delta import state as prior_state
from pg11245_batch_supplied_metric_label_fixture_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11254-current-batch-metric-label-delta-v1'
SOURCE='ef86a244b2f528a2d60bd0f22a94a853ce3146ff'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11228-current-web-supplied-metric-delta-v1/manifest.json','ab671737fc7a03397c1f9a84991fae82d844c2417b5dffa9c41b185d12ef1eee')
    d=data.read_checked(data.BASE/'PG11228-current-web-supplied-metric-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9035,2751,124]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11210-web-supplied-metric-fixture-six-compile-v1/manifest.json','11fb92b0b53b9dba26b93c8aa3e08c09c6c754b1b43fca1c20767ac270666d73')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11245-batch-supplied-metric-label-fixture-context-v1/manifest.json','3729fa303a0f91b6d048ff164de20009754650529ccea80666ca1818647d1ffb')
    rows=data.read_checked(data.BASE/'PG11245-batch-supplied-metric-label-fixture-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11247-batch-supplied-metric-label-fixture-context-post-v1/manifest.json','f9c21953fe2e41cc507e0bd249358ef8d3fe4c21af75c9771889f73d529cb817')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='3729fa303a0f91b6d048ff164de20009754650529ccea80666ca1818647d1ffb' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==34 and scope<=ids and len(scope&refs)==6 and not scope&pending
    assert len(fresh)==len(fresh_ids)==9 and len(reviewed)==8 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==25 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9010,2753,132,6257]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=34,newScopeFindings=9,replacedContextWarnings=6,newContextReferencesNet=2,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=9035,
        sourceDerivedRaw=9010,mainRaw=1512,testRaw=7498,totalPriorCorrections=399,sourceScopeCorrectionsAlreadyCounted=25,
        joinedContextWarnings=2753,sourceReboundCurrentWholePending=132,noCurrentReferenceInThisJoin=6257,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
