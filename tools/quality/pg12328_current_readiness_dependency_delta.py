"""Five exact original Test findings removed by measured selected static0; preserve all prior IDs."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12302_current_api_value_delta import state as before_value

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
OUT=data.BASE/'PG12328-current-readiness-dependency-delta-v1'

def state():
    ids,refs,pending=before_value()
    p=data.BASE/'PG12302-current-api-value-delta-v1/manifest.json';m=data.read_checked(p,'42c6f948a1af99fb682872dc1946d43710107dd6f8e0dac79c98a8380e84cebb');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8588,3114,662]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b');old=data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json','776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==2 and all('/src/test/java/' in p for p in changed)
    static=data.read_checked(data.BASE/'PG12316-readiness-dependency-static-v1/manifest.json','656d8b13e599bc581fd7410b9b13e7becc1903e2e5aa6a201621cb1874d82395');assert static['source']==SOURCE and static['actualExit']==0 and static['sourceHashes']==changed and all(r['findings']==r['processingErrors']==0 for r in static['reports'].values())
    completion=data.read_checked(data.BASE/'PG12324-readiness-dependency-completion-v1/manifest.json','68454b5e1108a07a768670feafb76a6b34ae809a3c27338eaec674421cecd4d3');assert completion['source']==SOURCE and completion['actualExit']==0 and completion['actual']['tests']==4
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope={r['id'] for r in original if r['path'] in changed}&ids
    assert scope=={'PMD-00859','PMD-00860','PMD-00861','PMD-00862','PMD-07636'} and not scope&(refs|pending)
    assert all(r['rule']=='AvoidDuplicateLiterals' and r['inputSha256']==old['begin']['inputHashes'][r['path']] for r in original if r['id'] in scope)
    current=ids-scope;assert len(current)==8583 and len({r['id'] for r in original}-current)==834 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=sorted(scope),addedFindingIds=[],originalScopeFindings=len(scope),oldScopeFindings=len(scope),newScopeFindings=0,priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=0,priorScopePending=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=len(changed),otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8588,sourceDerivedRaw=len(current),mainRaw=1512,testRaw=7071,totalPriorCorrections=834,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=len(scope),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(current-refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
