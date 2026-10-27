"""Bind12 Batch pure value fixes and1 current loader reference; retain prior775 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12180_current_audit_fixture_delta import state as before_jms
from pg11054_api_request_context import original_match

SOURCE='4b5f6faa078be348132a6ece9140b0c1a31d7907'
OUT=data.BASE/'PG12210-current-audit-metric-delta-v1'
CONTEXT_SHA='12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2'

def state():
    ids,refs,pending=before_jms();p=data.BASE/'PG12180-current-audit-fixture-delta-v1/manifest.json';m=data.read_checked(p,'527eeb1e6c9351cf3c466becfb75226096559f0db2aa8c46c68f9930264f641e');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8617,3103,645]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12194-audit-metric-six-compile-v1/manifest.json','971ee001e169f9fa05df627e0cd0789704518d952105c27328eabf86ebd4adff');old=data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json','462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12198-audit-metric-static-v1';static=data.read_checked(sp/'manifest.json','a10133ca7dedd88083f8f39c8b96b0af1cde5ffc161655dc8feb3591b10d8255');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12201-audit-metric-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==5 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']]
        assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==14 and len(fresh)==len(fresh_ids)==5 and set(contexts)==fresh_ids and len(removed)==9 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidFieldNameMatchingMethodName','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    assert len(scope&refs)==5 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert len(current)==8608 and len({r['id'] for r in original}-current)==809 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=27,oldScopeFindings=14,newScopeFindings=5,priorScopeCorrectionsRetained=13,replacedContextWarnings=5,newContextReferencesNet=0,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=8617,sourceDerivedRaw=8608,mainRaw=1512,testRaw=7096,totalPriorCorrections=809,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=9,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8608-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
