"""Bind23 API/Web scrape fixes and5 current references; retain prior719 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12030_current_web_business_record_rebind import state as before_jms
from pg11054_api_request_context import original_match

SOURCE='913eedbc22a42fa077c2c408baa7d63f7004abc3'
OUT=data.BASE/'PG12060-current-api-web-scrape-fixture-delta-v1'
CONTEXT_SHA='8a1d76ee89e42839efa9b827a5c563825fec0bb04537ba46b8d89b3546c113a0'

def state():
    ids,refs,pending=before_jms();p=data.BASE/'PG12030-current-web-business-record-rebind-v1/manifest.json';m=data.read_checked(p,'50e64f71443493a53d77da457f82b6d7c08a2a871e7bdcabb70d1347c2a86b47');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8698,3100,621]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12044-api-web-scrape-fixture-six-compile-v1/manifest.json','fe989f6495c165f388cd4cc916da0ea8ed6901420c61d7ada7e2a742f8e6b672');old=data.read_checked(data.BASE/'PG12016-web-business-record-six-compile-v1/manifest.json','214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12048-api-web-scrape-fixture-static-v1';static=data.read_checked(sp/'manifest.json','8611c53e8258e30c485fb8fc95ced1ec763286324b0f3ab524bf2bc844d28b40');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12053-api-web-scrape-fixture-context-v2';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==5 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==28 and len(fresh)==len(fresh_ids)==5 and fresh_ids==set(contexts) and len(removed)==23 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    assert len(scope&refs)==4 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8675 and len({r['id'] for r in original}-current)==742 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=28,oldScopeFindings=28,newScopeFindings=5,priorScopeCorrectionsRetained=0,replacedContextWarnings=4,newContextReferencesNet=1,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8698,sourceDerivedRaw=8675,mainRaw=1512,testRaw=7163,totalPriorCorrections=742,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=23,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8675-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
