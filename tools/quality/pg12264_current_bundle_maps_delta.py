"""Add seven unchanged Bundle/collector Main applicability references; retain every raw warning and no runtime credit."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12250_current_main_local_maps_delta import state as prior_state

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12264-current-bundle-maps-delta-v1'
CONTEXT='8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05'

def state():
    ids,refs,pending=prior_state();p=data.BASE/'PG12250-current-main-local-maps-delta-v1'
    m=data.read_checked(p/'manifest.json','fb90f713360f60c7e10d089ce428ff2dd158a1e65bd3397b8aa3080cd9915738');d=data.read_checked(p/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8597,3107,653]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    p=data.BASE/'PG12260-bundle-maps-context-v1';context=data.read_checked(p/'manifest.json',CONTEXT);rows=data.read_checked(p/'review.json',context['reviewSha256'])['rows']
    post=data.read_checked(data.BASE/'PG12262-bundle-maps-post-v1/manifest.json','61523ad29196dabd3f8084ec237515022d661109bdcd00bce24c57b84f495297')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0 and post['metadataNegativeVectors']==20 and post['ownershipNegativeVectors']==4
    selected={r['id'] for r in rows};assert selected=={'PMD-02774','PMD-02775','PMD-02776','PMD-02777','PMD-06190','PMD-06191','PMD-06194'} and selected<=ids and not selected&(refs|pending)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');originals={r['id']:r for r in original};fresh=[]
    for row in rows:
        original_row=originals[row['id']];path=row['path'];sha=normal['begin']['inputHashes'][path]
        assert row['sourceKind']=='MAIN' and '/src/main/java/' in path and row['sourceSha256']==sha==original_row['inputSha256'] and row['attributes']==original_row['attributes'] and row['currentWholeJoinPending'] and row['productTestsExecutedByReview']==0
        fresh.append(dict(id=row['id'],path=path,source=SOURCE,sourceKind='MAIN',currentInputSha256=sha,rule=row['rule'],attributes=row['attributes'],originalRowSha256=row['originalRowSha256'],contextManifestSha256=CONTEXT,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    refs|=selected;pending|=selected;assert len(refs)==3114 and len(pending)==660 and len({r['id'] for r in original}-ids)==820
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourceInputHashes={r['path']:r['sourceSha256'] for r in rows},callerSourceInputHashes={r['collectorCaller']['path']:r['collectorCaller']['sourceSha256'] for r in rows if r['collectorCaller']},freshRows=fresh,removedFindingIds=[],addedFindingIds=[],originalScopeFindings=7,oldScopeFindings=7,newScopeFindings=7,priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=7,priorScopePending=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,reviewedSourcePaths=2,callerSourcePaths=1,otherSourcePathsUnchanged=1810,originalRaw=9409,priorDerivedRaw=8597,sourceDerivedRaw=8597,mainRaw=1512,testRaw=7085,totalPriorCorrections=820,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
