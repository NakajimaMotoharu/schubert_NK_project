"""Add four unchanged Main applicability references, never raw correction or runtime credit."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12240_current_check_health_delta import state as prior_state

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12250-current-main-local-maps-delta-v1'
CONTEXT='1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e'

def state():
    ids,refs,pending=prior_state();p=data.BASE/'PG12240-current-check-health-delta-v1'
    m=data.read_checked(p/'manifest.json','9f37c0d8983be65a362088e8adbf47c021199824d3055baf86ef36a73167a70a');d=data.read_checked(p/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8597,3103,649]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    p=data.BASE/'PG12246-main-local-maps-context-v1';context=data.read_checked(p/'manifest.json',CONTEXT);rows=data.read_checked(p/'review.json',context['reviewSha256'])['rows']
    post=data.read_checked(data.BASE/'PG12248-main-local-maps-post-v1/manifest.json','6167dcf7e8671527f16ec20d4c6f0f2fe2b02257a9b404a03719bd588b900fb3')
    assert context['source']==post['source']==SOURCE and context['actualExit']==post['actualExit']==0 and post['metadataNegativeVectors']==14
    selected={r['id'] for r in rows};assert selected=={'PMD-00122','PMD-07323','PMD-03094','PMD-03111'} and selected<=ids and not selected&(refs|pending)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');originals={r['id']:r for r in original};fresh=[]
    for row in rows:
        original_row=originals[row['id']];path=row['path'];sha=normal['begin']['inputHashes'][path]
        assert row['sourceKind']=='MAIN' and '/src/main/java/' in path and row['sourceSha256']==sha==original_row['inputSha256'] and row['attributes']==original_row['attributes'] and row['currentWholeJoinPending'] and row['productTestsExecutedByReview']==0
        fresh.append(dict(id=row['id'],path=path,source=SOURCE,sourceKind='MAIN',currentInputSha256=sha,rule=row['rule'],attributes=row['attributes'],originalRowSha256=row['originalRowSha256'],contextManifestSha256=CONTEXT,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    refs|=selected;pending|=selected;assert len(refs)==3107 and len(pending)==653 and len({r['id'] for r in original}-ids)==820
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourceInputHashes={r['path']:r['sourceSha256'] for r in rows},freshRows=fresh,removedFindingIds=[],addedFindingIds=[],originalScopeFindings=4,oldScopeFindings=4,newScopeFindings=4,priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=4,priorScopePending=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,reviewedSourcePaths=4,otherSourcePathsUnchanged=1810,originalRaw=9409,priorDerivedRaw=8597,sourceDerivedRaw=8597,mainRaw=1512,testRaw=7085,totalPriorCorrections=820,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
