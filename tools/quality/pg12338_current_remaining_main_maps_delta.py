"""Append eight unchanged Main applicability references; no raw correction or runtime credit."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12328_current_readiness_dependency_delta import state as before_pure

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
OUT=data.BASE/'PG12338-current-remaining-main-maps-delta-v1'
CONTEXT='4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e'

def state():
    ids,refs,pending=before_pure();p=data.BASE/'PG12328-current-readiness-dependency-delta-v1/manifest.json';m=data.read_checked(p,'354f683868a39166216cc5cd5a2498f27392567c609b87140fcfda0921851c4f');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8583,3114,662]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b');assert normal['source']==SOURCE and normal['actualExit']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    p=data.BASE/'PG12334-remaining-main-maps-context-v1';cm=data.read_checked(p/'manifest.json',CONTEXT);review=data.read_checked(p/'review.json',cm['reviewSha256']);rows=review['rows']
    post=data.read_checked(data.BASE/'PG12336-remaining-main-maps-post-v1/manifest.json','e180597ce36baed2150998a199c08d182ca79f147fd08f8b1ef36abf36b02db0');assert cm['source']==post['source']==SOURCE and cm['actualExit']==post['actualExit']==0 and post['metadataNegativeVectors']==28
    selected={r['id'] for r in rows};assert len(selected)==len(rows)==cm['rawRetained']==cm['sourceContexts']==8 and selected<=ids and not selected&(refs|pending)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');originals={r['id']:r for r in original};fresh=[]
    for row in rows:
        r=originals[row['id']];path=row['path'];sha=normal['begin']['inputHashes'][path]
        assert row['sourceKind']=='MAIN' and '/src/main/java/' in path and row['sourceSha256']==r['inputSha256']==sha and row['attributes']==r['attributes'] and row['currentWholeJoinPending'] and row['productTestsExecutedByReview']==0
        fresh.append(dict(id=row['id'],path=path,source=SOURCE,sourceKind='MAIN',currentInputSha256=sha,rule=row['rule'],attributes=row['attributes'],originalRowSha256=row['originalRowSha256'],contextManifestSha256=CONTEXT,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    refs|=selected;pending|=selected;assert len(refs)==3122 and len(pending)==670 and len({r['id'] for r in original}-ids)==834
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},reviewedSourceInputHashes={r['path']:r['sourceSha256'] for r in rows},supportValueSourceHashes=review['supportValueSourceHashes'],freshRows=fresh,removedFindingIds=[],addedFindingIds=[],originalScopeFindings=len(selected),oldScopeFindings=len(selected),newScopeFindings=len(selected),priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=len(selected),priorScopePending=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=0,reviewedSourcePaths=2,supportSourcePaths=3,otherSourcePathsUnchanged=1810,originalRaw=9409,priorDerivedRaw=8583,sourceDerivedRaw=8583,mainRaw=1512,testRaw=7071,totalPriorCorrections=834,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
