"""Join8 reauthenticated reasons and40 new source point reviews; raw count is unchanged."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11564_current_batch_repository_reason_delta import state as before_two_repository_review

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11574-current-four-repository-reason-delta-v1'

def state():
    ids,refs,pending=before_two_repository_review()
    p=data.BASE/'PG11564-current-batch-repository-reason-delta-v1/manifest.json';m=data.read_checked(p,'7f74d22280372600bb6c8287e831f2759108756310473dc64c7caac364042a0a');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,2937,378]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    cp=data.BASE/'PG11570-batch-four-repository-source-review-v1/manifest.json';context=data.read_checked(cp,'21a66250b1d54e19576b84b3144a2ee4395925b538401a07934eaf080c2bd77b')
    review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    post=data.read_checked(data.BASE/'PG11572-batch-four-repository-source-review-post-v1/manifest.json','5fb3dcbaac87a9518a42ef7c292c6cfe1d5465d6919139922042950270d4d522')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0
    assert review['reauthenticatedHistoricalReasons']==8 and review['newIndividualDispositions']==40
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['mainSourceHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    reviewed={r['id'] for r in review['rows']};paths={r['path'] for r in review['rows']};scope={r['id'] for r in original if r['path'] in paths and r['rule'] in ('CloseResource','AvoidCatchingGenericException','DoNotThrowExceptionInFinally')}&ids
    assert len(scope)==len(reviewed)==48 and scope==reviewed and not scope&refs and not scope&pending
    fresh=[]
    for row in review['rows']:
        assert not row['oldRuntimeReassigned'] and row['coverage'] is None and row['productTestsExecuted']==0 and row['rawWarningRetained']
        fresh.append(dict(id=row['id'],path=row['path'],source=SOURCE,sourceKind='MAIN',currentInputSha256=row['sourceSha256'],attributes=row['attributes'],identityRowSha256=row['originalRowSha256'],
            contextManifestSha256='21a66250b1d54e19576b84b3144a2ee4395925b538401a07934eaf080c2bd77b',disposition=row['disposition'],reasonOrigin=row['reasonOrigin'],
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    cr=refs|reviewed;cpending=pending|reviewed
    assert [len(ids),len(cr),len(cpending),len(ids-cr)]==[8896,2985,426,5911]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourcePaths=sorted(paths),freshRows=fresh,removedFindingIds=[],addedFindingIds=[],oldScopeFindings=48,newScopeFindings=48,
        reauthenticatedHistoricalReasons=8,newSourcePointReviews=40,replacedContextWarnings=0,newContextReferencesNet=48,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,otherSourcePathsUnchanged=1810,
        originalRaw=9409,priorDerivedRaw=8896,sourceDerivedRaw=8896,mainRaw=1512,testRaw=7384,totalPriorCorrections=521,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,
        sourceScopeCorrectionsAlreadyCounted=0,reauthenticatedHistoricalReasons=8,newSourcePointReviews=40,joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
