"""Rebind current12 source/2 thread references; preserve719 corrections and all8 introduced diagnostics and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12000_current_web_business_wire_fixture_delta import state as before_business
from pg11054_api_request_context import original_match

SOURCE='54e84fe04836dd88c3adfda5ac3f010eb591a7ee'
OUT=data.BASE/'PG12030-current-web-business-record-rebind-v1'
CONTEXT_SHA='4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13'

def state():
    ids,refs,pending=before_business();p=data.BASE/'PG12000-current-web-business-wire-fixture-delta-v1/manifest.json';m=data.read_checked(p,'d80140f38a55b3f2c554fb88f18bf82e18665233697381e0c0440fc8ea43401f');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8698,3100,621]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12016-web-business-record-six-compile-v1/manifest.json','214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a');old=data.read_checked(data.BASE/'PG11984-web-business-wire-fixture-six-compile-v1/manifest.json','ba7eb4d008ea6968016bcc4767cdc552d294def6e13f9ac3c0e232bbe34c17f8')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12020-web-business-record-static-v1';static=data.read_checked(sp/'manifest.json','3bfc240dc4772cdaec9c574f9e0527fdab3d6ba89d28872161c2de5aaaf3ae3b');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12023-web-business-record-owner-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==2 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==2 and len(fresh)==len(fresh_ids)==2 and fresh_ids==set(contexts) and len(removed)==0 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidFieldNameMatchingMethodName') for r in original if r['id'] in removed)
    assert len(scope&refs)==2 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8698 and len({r['id'] for r in original}-current)==719 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=26,oldScopeFindings=2,newScopeFindings=2,priorScopeCorrectionsRetained=24,replacedContextWarnings=2,newContextReferencesNet=0,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8698,sourceDerivedRaw=8698,mainRaw=1512,testRaw=7186,totalPriorCorrections=719,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=24,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8698-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
