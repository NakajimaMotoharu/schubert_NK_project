"""Join26 reauthenticated reasons and70 new source point reviews; raw count is unchanged."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11552_current_memory_http_guard_delta import state as before_memory_guard

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11564-current-batch-repository-reason-delta-v1'

def state():
    ids,refs,pending=before_memory_guard()
    p=data.BASE/'PG11552-current-memory-http-guard-delta-v1/manifest.json';m=data.read_checked(p,'27544edc188e17ec6ec38a7222dc8403298827e25762c67e56cee865e7b1e0bc');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,2841,282]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    cp=data.BASE/'PG11560-batch-two-repository-reason-rebind-v2/manifest.json';context=data.read_checked(cp,'eee2f10894540f8516758a60c5c6fae0f92754f977db2f83cd2b0056cc32d879')
    review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    post=data.read_checked(data.BASE/'PG11562-batch-two-repository-reason-rebind-post-v2/manifest.json','b4a9d2e02875101f6c063227e56478747cd2ea6b569a0e0b77716ad313acc99a')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0
    assert review['reauthenticatedHistoricalReasons']==26 and review['newIndividualDispositions']==70
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['mainSourceHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    reviewed={r['id'] for r in review['rows']};paths={r['path'] for r in review['rows']};scope={r['id'] for r in original if r['path'] in paths}&ids
    assert len(scope)==len(reviewed)==96 and scope==reviewed and not scope&refs and not scope&pending
    fresh=[]
    for row in review['rows']:
        assert not row['oldRuntimeReassigned'] and row['coverage'] is None and row['productTestsExecuted']==0 and row['rawWarningRetained']
        fresh.append(dict(id=row['id'],path=row['path'],source=SOURCE,sourceKind='MAIN',currentInputSha256=row['sourceSha256'],attributes=row['attributes'],identityRowSha256=row['originalRowSha256'],
            contextManifestSha256='eee2f10894540f8516758a60c5c6fae0f92754f977db2f83cd2b0056cc32d879',disposition=row['disposition'],reasonOrigin=row['reasonOrigin'],
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    cr=refs|reviewed;cpending=pending|reviewed
    assert [len(ids),len(cr),len(cpending),len(ids-cr)]==[8896,2937,378,5959]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourcePaths=sorted(paths),freshRows=fresh,removedFindingIds=[],addedFindingIds=[],oldScopeFindings=96,newScopeFindings=96,
        reauthenticatedHistoricalReasons=26,newSourcePointReviews=70,replacedContextWarnings=0,newContextReferencesNet=96,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,otherSourcePathsUnchanged=1810,
        originalRaw=9409,priorDerivedRaw=8896,sourceDerivedRaw=8896,mainRaw=1512,testRaw=7384,totalPriorCorrections=521,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,
        sourceScopeCorrectionsAlreadyCounted=0,reauthenticatedHistoricalReasons=26,newSourcePointReviews=70,joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
