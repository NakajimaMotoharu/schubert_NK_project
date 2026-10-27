"""Join four-source presentation findings to immutable IDs; no analyzer or product replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11148_current_web_presentation_delta import state as prior_state
from pg11165_api_metric_fixture_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11174-current-api-supplied-metric-delta-v1'
SOURCE='aafcc38d2d48627e10f816dd45bfaeb20bf5e415'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11148-current-web-presentation-delta-v1/manifest.json','154c363c7f6d24000346bdec41d970fe02cf39c8f6c7bf13ed2554d8eb9222c1')
    d=data.read_checked(data.BASE/'PG11148-current-web-presentation-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9134,2739,90]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11132-web-presentation-six-compile-v1/manifest.json','6ba6867e803958aa47837d6628faeecdf42917be8d23bff7a38b5e1b18579eee')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==4 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11165-api-metric-fixture-context-v1/manifest.json','3b02041b948f03e6993b9bf2603bf943597c252bd8e0375ee5e5c12b3a761813')
    rows=data.read_checked(data.BASE/'PG11165-api-metric-fixture-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11167-api-metric-fixture-context-post-v1/manifest.json','fd3ac323594856c0d1b417d259957e845907bdfabe3c96c7c8fa890c458d009c')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='3b02041b948f03e6993b9bf2603bf943597c252bd8e0375ee5e5c12b3a761813',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==55 and scope<=ids and len(scope&refs)==8 and not scope&pending
    assert len(fresh)==len(fresh_ids)==len(reviewed)==12 and fresh_ids==reviewed
    removed=scope-fresh_ids
    assert len(removed)==43 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9091,2743,102,6348]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=55,newScopeFindings=12,replacedContextWarnings=8,newContextReferencesNet=4,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=9134,
        sourceDerivedRaw=9091,mainRaw=1512,testRaw=7579,totalPriorCorrections=318,sourceScopeCorrectionsAlreadyCounted=43,
        joinedContextWarnings=2743,sourceReboundCurrentWholePending=102,noCurrentReferenceInThisJoin=6348,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
