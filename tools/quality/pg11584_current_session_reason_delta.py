"""Join42 reauthenticated reasons and two new source point reviews; raw count is unchanged."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11574_current_four_repository_reason_delta import state as before_four_repository_review

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11584-current-session-reason-delta-v1'

def state():
    ids,refs,pending=before_four_repository_review()
    p=data.BASE/'PG11574-current-four-repository-reason-delta-v1/manifest.json';m=data.read_checked(p,'7d8654ec83c6d8846b109ecb4a6cc11101fb13e904b0a722d96a727b2d316ffe');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,2985,426]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    cp=data.BASE/'PG11580-batch-session-source-review-v1/manifest.json';context=data.read_checked(cp,'198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc')
    review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    post=data.read_checked(data.BASE/'PG11582-batch-session-source-review-post-v1/manifest.json','7f2130d91fa6fe4e4b1b3846455218702099d19effb32b6e6d361219300c57a3')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0
    assert review['reauthenticatedHistoricalReasons']==42 and review['newIndividualDispositions']==2
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['mainSourceHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    reviewed={r['id'] for r in review['rows']};paths={r['path'] for r in review['rows']};scope={r['id'] for r in original if r['path'] in paths and r['rule']!='DoNotUseThreads'}&ids
    assert len(scope)==len(reviewed)==44 and scope==reviewed and not scope&refs and not scope&pending
    fresh=[]
    for row in review['rows']:
        assert not row['oldRuntimeReassigned'] and row['coverage'] is None and row['productTestsExecuted']==0 and row['rawWarningRetained']
        fresh.append(dict(id=row['id'],path=row['path'],source=SOURCE,sourceKind='MAIN',currentInputSha256=row['sourceSha256'],attributes=row['attributes'],identityRowSha256=row['originalRowSha256'],
            contextManifestSha256='198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc',disposition=row['disposition'],reasonOrigin=row['reasonOrigin'],
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    cr=refs|reviewed;cpending=pending|reviewed
    assert [len(ids),len(cr),len(cpending),len(ids-cr)]==[8896,3029,470,5867]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourcePaths=sorted(paths),freshRows=fresh,removedFindingIds=[],addedFindingIds=[],oldScopeFindings=44,newScopeFindings=44,
        reauthenticatedHistoricalReasons=42,newSourcePointReviews=2,replacedContextWarnings=0,newContextReferencesNet=44,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,otherSourcePathsUnchanged=1810,
        originalRaw=9409,priorDerivedRaw=8896,sourceDerivedRaw=8896,mainRaw=1512,testRaw=7384,totalPriorCorrections=521,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,
        sourceScopeCorrectionsAlreadyCounted=0,reauthenticatedHistoricalReasons=42,newSourcePointReviews=2,joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
