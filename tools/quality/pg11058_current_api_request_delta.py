"""Current F03 small API source delta; no analyzer or target test replay."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11028_current_remaining_form_delta import parent_state
from pg11054_api_request_context import inputs, original_match

OUT=data.BASE/'PG11058-current-api-request-delta-v1'
POST=data.BASE/'PG11060-current-api-request-delta-post-v1'
SOURCE='9b255cbe300d1feffeeee076cfa5af318c9b1bb1'


def state():
    parent=data.read_checked(data.BASE/'PG11028-current-remaining-form-delta-v1/manifest.json','a1b84233e2748889d2e659c3b611d6f8560685f5e7d84edb9a3e2018e9bb6f49')
    delta=data.read_checked(data.BASE/'PG11028-current-remaining-form-delta-v1/delta.json',parent['deltaSha256'])
    ids,refs,pending=parent_state()
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    ids-=set(delta['removedFindingIds'])
    refs=(refs-scope)|{r['id'] for r in delta['freshRows']}
    pending=(pending-scope)|{r['id'] for r in delta['freshRows']}
    assert [len(ids),len(refs),len(pending)]==[9204,2728,60]
    return ids,refs,pending


def expected():
    ids,refs,pending=state()
    normal,original,actual=inputs()
    old=data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json','5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert len(current)==1810
    changed={p:h for p,h in current.items() if old['begin']['inputHashes'][p]!=h}
    assert len(changed)==4 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11054-api-request-context-v1/manifest.json','88ede17e3d71b67ce4f761051ed20f07f4f11a67091a7af4038955da060ec668')
    rows=data.read_checked(data.BASE/'PG11054-api-request-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11056-api-request-context-post-v1/manifest.json','9cd036c5876a05d45944f30e5555f78e131bfcfe2e98cf0840c75d1d16cf4ee0')
    assert post['actualExit']==0 and post['source']==context['source']==SOURCE
    context_ids={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        row=original_match(path,node,original,actual)
        fresh.append(dict(id=row['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],
            rule=row['rule'],attributes=dict(node.attrib),originalRowSha256=row['rowSha256'],
            contextManifestSha256='88ede17e3d71b67ce4f761051ed20f07f4f11a67091a7af4038955da060ec668' if row['id'] in context_ids else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if row['id'] in context_ids else 'UNCLASSIFIED_SHARED_FIELD',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    assert len(fresh)==len(fresh_ids)==17 and context_ids<=fresh_ids and len(context_ids)==16
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==31 and scope<=ids and len(scope&refs)==7 and not scope&pending
    removed=scope-fresh_ids
    by_id={r['id']:r for r in original}
    assert len(removed)==14 and sum(by_id[i]['rule']=='AvoidDuplicateLiterals' for i in removed)==12
    assert sorted(by_id[i]['rule'] for i in removed if by_id[i]['rule']!='AvoidDuplicateLiterals')==['AvoidFieldNameMatchingMethodName','AvoidLiteralsInIfCondition']
    result=dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        sourceDerivedRaw=len(ids-removed),joinedContextWarnings=len((refs-scope)|context_ids),
        sourceReboundCurrentWholePending=len((pending-scope)|context_ids),
        noCurrentReferenceInThisJoin=len((ids-removed)-((refs-scope)|context_ids)))
    assert [result[k] for k in ('sourceDerivedRaw','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin')]==[9190,2737,76,6453]
    return result


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    result=expected()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        originalRaw=9409,priorDerivedRaw=9204,sourceDerivedRaw=9190,mainRaw=1512,testRaw=7678,totalPriorCorrections=219,
        sourceScopeCorrectionsAlreadyCounted=14,oldScope31=True,newScope17=True,sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,
        joinedContextWarnings=2737,sourceReboundCurrentWholePending=76,noCurrentReferenceInThisJoin=6453,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
