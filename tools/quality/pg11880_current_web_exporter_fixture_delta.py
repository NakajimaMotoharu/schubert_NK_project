"""Twelve actual current fixture corrections, no contexts added and no product replay."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11850_current_mq_media_collector_value_delta import state as before_collectors

SOURCE='06685adcf32c8583c80cb9c3e4d06d547ada486c'
OUT=data.BASE/'PG11880-current-web-exporter-fixture-delta-v1'

def state():
    ids,refs,pending=before_collectors();p=data.BASE/'PG11850-current-mq-media-collector-value-delta-v1';m=data.read_checked(p/'manifest.json','8a0764023d4bcf3d3a4781fc8f38450d11b98141ce5af6fdea33ff763e976e42');d=data.read_checked(p/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed;assert [len(ids),len(refs),len(pending)]==[8791,3091,606]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG11864-web-exporter-fixture-six-compile-v1/manifest.json','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d');old=data.read_checked(data.BASE/'PG11834-mq-media-collector-value-six-compile-v1/manifest.json','878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b');hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and normal['actualExit']==0 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items());java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11868-web-exporter-fixture-static-v1';m=data.read_checked(sp/'manifest.json','3b08df0c3b89baf7b636f007498c861760492ed0b95056d9b324060fb2178ca5');assert m['actualExit']==0 and m['source']==SOURCE and set(m['sourceHashes'])==set(changed)
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        raw=(sp/(label+'.xml')).read_bytes();assert data.sha(raw)==m['reports'][label]['sha256'];assert not any(n.tag.rpartition('}')[2] in (tag,'error','configerror') for n in ET.fromstring(raw).iter())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[r for r in original if r['path'] in changed and r['id'] in ids];removed={r['id'] for r in rows};assert len(removed)==12 and sum(r['rule']=='AvoidDuplicateLiterals' for r in rows)==11 and sum(r['rule']=='AvoidFieldNameMatchingMethodName' for r in rows)==1 and not removed&(refs|pending)
    current=ids-removed;assert len(current)==8779 and len({r['id'] for r in original}-current)==638 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,removed,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,removed,refs,pending=inputs();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=12,oldScopeFindings=12,newScopeFindings=0,priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=0,priorScopePending=0,newProductExecutions=0));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=8791,sourceDerivedRaw=8779,mainRaw=1512,testRaw=7267,totalPriorCorrections=638,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=12,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8779-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
