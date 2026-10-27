"""Join22 reauthenticated nonempty reasons without new source dispositions; raw count is unchanged."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11594_current_admission_reason_delta import state as before_admission_review

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11604-current-remaining-main-reason-delta-v2'

def state():
    ids,refs,pending=before_admission_review()
    p=data.BASE/'PG11594-current-admission-reason-delta-v1/manifest.json';m=data.read_checked(p,'877f695001a733ead184d078282c4f745836b7261b4628c09782919a1917f4b8');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,3048,489]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    cp=data.BASE/'PG11600-remaining-main-source-reauth-v4/manifest.json';context=data.read_checked(cp,'09fbb963cf1a85c92357ffc42dea91852a443e4d1175e606f5cd82f160ffa442')
    review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    post=data.read_checked(data.BASE/'PG11602-remaining-main-source-reauth-post-v4/manifest.json','3f417e8b4e92d40d708cf4d0651b7d8b10a04f0272173fb84701e65131def4fd')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0
    assert review['reauthenticatedHistoricalReasons']==22 and review['newIndividualDispositions']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['mainSourceHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    reviewed={r['id'] for r in review['rows']};paths={r['path'] for r in review['rows']};scope={r['id'] for r in original if r['id'] in reviewed and r['path'] in paths}&ids
    assert len(scope)==len(reviewed)==22 and scope==reviewed and not scope&refs and not scope&pending
    fresh=[]
    for row in review['rows']:
        assert not row['oldRuntimeReassigned'] and row['coverage'] is None and row['productTestsExecuted']==0 and row['rawWarningRetained']
        fresh.append(dict(id=row['id'],path=row['path'],source=SOURCE,sourceKind='MAIN',currentInputSha256=row['sourceSha256'],attributes=row['attributes'],identityRowSha256=row['originalRowSha256'],
            contextManifestSha256='09fbb963cf1a85c92357ffc42dea91852a443e4d1175e606f5cd82f160ffa442',disposition=row['disposition'],reasonOrigin=row['reasonOrigin'],
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    cr=refs|reviewed;cpending=pending|reviewed
    assert [len(ids),len(cr),len(cpending),len(ids-cr)]==[8896,3070,511,5826]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourcePaths=sorted(paths),freshRows=fresh,removedFindingIds=[],addedFindingIds=[],oldScopeFindings=22,newScopeFindings=22,
        reauthenticatedHistoricalReasons=22,newSourcePointReviews=0,replacedContextWarnings=0,newContextReferencesNet=22,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,otherSourcePathsUnchanged=1810,
        originalRaw=9409,priorDerivedRaw=8896,sourceDerivedRaw=8896,mainRaw=1512,testRaw=7384,totalPriorCorrections=521,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,
        sourceScopeCorrectionsAlreadyCounted=0,reauthenticatedHistoricalReasons=22,newSourcePointReviews=0,joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
