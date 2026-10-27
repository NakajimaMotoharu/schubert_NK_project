"""Join API/Web source guard actual50to16 and12 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11338_current_batch_source_guard_delta import state as prior_state
from pg11355_api_web_source_guard_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11364-current-api-web-source-guard-delta-v1'
SOURCE='d4b5507ba6a76a85c23806e5604a0278f1795f37'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11338-current-batch-source-guard-delta-v1/manifest.json','7065e59aec2e111a7620f9e543c07e66d1d58d01ee89026dc08af63a778b83e4')
    d=data.read_checked(data.BASE/'PG11338-current-batch-source-guard-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[8958,2755,158]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11322-batch-source-guard-six-compile-v1/manifest.json','066e1c301187c43224e8ab120c50889ef8a832f48de3fe4406aa7e533ac14e27')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11355-api-web-source-guard-context-v1/manifest.json','24f93b068aa960e1d488607922591b76c1997a62ecd93f4717a48623c8d9b11a')
    rows=data.read_checked(data.BASE/'PG11355-api-web-source-guard-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11357-api-web-source-guard-context-post-v1/manifest.json','93eb89d97be4a1621d67a0aa3af54c9ada11ec46494342769f6f341f15208a33')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='24f93b068aa960e1d488607922591b76c1997a62ecd93f4717a48623c8d9b11a' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    scope=original_scope&ids
    assert len(original_scope)==len(scope)==50 and len(scope&refs)==12 and len(scope&pending)==0
    assert all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in original_scope-scope)
    assert len(fresh)==len(fresh_ids)==16 and len(reviewed)==12 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==34 and all(r['rule'] in ('CloseResource','AvoidDuplicateLiterals') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[8924,2755,170,6169]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        originalScopeFindings=50,previouslyRemovedIds=sorted(original_scope-scope),oldScopeFindings=50,newScopeFindings=16,replacedContextWarnings=12,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8958,
        sourceDerivedRaw=8924,mainRaw=1512,testRaw=7412,totalPriorCorrections=485,sourceScopeCorrectionsAlreadyCounted=34,
        joinedContextWarnings=2755,sourceReboundCurrentWholePending=170,noCurrentReferenceInThisJoin=6169,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
