"""Join current full-payload43to39 and30 contexts; retain prior Batch6 removal to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11364_current_api_web_source_guard_delta import state as prior_state
from pg11387_full_payload_guard_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11396-current-full-payload-guard-delta-v1'
SOURCE='4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11364-current-api-web-source-guard-delta-v1/manifest.json','bcfe5e858e6f0c5b51d9955f25dba47a4830fd47ef364bb3561c6a7f3be23530')
    d=data.read_checked(data.BASE/'PG11364-current-api-web-source-guard-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[8924,2755,170]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json','46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11387-full-payload-guard-context-v1/manifest.json','05d0ea5697dfe458af05045250467e076cda73da892e068113e8a142782c3321')
    rows=data.read_checked(data.BASE/'PG11387-full-payload-guard-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11389-full-payload-guard-context-post-v1/manifest.json','93ae0b82507de121a9cf34acbb041026319c7a8f6e1b3288c53bf039780652a4')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='05d0ea5697dfe458af05045250467e076cda73da892e068113e8a142782c3321' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    scope=original_scope&ids
    assert len(original_scope)==49 and len(scope)==43 and len(scope&refs)==28 and len(scope&pending)==6
    assert all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in original_scope-scope)
    assert len(fresh)==len(fresh_ids)==39 and len(reviewed)==30 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==4 and all(r['rule']=='CloseResource' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[8920,2757,194,6163]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        originalScopeFindings=49,previouslyRemovedIds=sorted(original_scope-scope),oldScopeFindings=43,newScopeFindings=39,replacedContextWarnings=28,newContextReferencesNet=2,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=8924,
        sourceDerivedRaw=8920,mainRaw=1512,testRaw=7408,totalPriorCorrections=489,sourceScopeCorrectionsAlreadyCounted=4,
        joinedContextWarnings=2757,sourceReboundCurrentWholePending=194,noCurrentReferenceInThisJoin=6163,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
