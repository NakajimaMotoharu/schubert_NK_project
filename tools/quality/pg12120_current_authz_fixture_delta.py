"""Bind10 Mock Servlet authorization fixes and3 current references; retain prior765 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12090_current_media_wire_fixture_delta import state as before_jms
from pg11054_api_request_context import original_match

SOURCE='ee82637a750105243ddeac665c61d27a781e5cf1'
OUT=data.BASE/'PG12120-current-authz-fixture-delta-v1'
CONTEXT_SHA='6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22'

def state():
    ids,refs,pending=before_jms();p=data.BASE/'PG12090-current-media-wire-fixture-delta-v1/manifest.json';m=data.read_checked(p,'a7a15a3a66183c8762b9b4e13639b352045990a31c019de03fc49a99ef888a55');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8652,3101,638]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12104-authz-fixture-six-compile-v1/manifest.json','1cffddad23dd78451013a1bb325a7e84682d733fb80d57f3205279d12d9774f9');old=data.read_checked(data.BASE/'PG12074-media-wire-fixture-six-compile-v1/manifest.json','2a15c3279d00cd2509f156e85442ae46124a3f1c5e8ea1b6b9ed0c82e29e81b0')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12109-authz-fixture-static-v2';static=data.read_checked(sp/'manifest.json','debf7b4ce804a32e6b5c797e4fc5b1a2c129bf7caa065a1891487e50fa31ff6b');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12111-authz-fixture-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==3 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==13 and len(fresh)==len(fresh_ids)==3 and fresh_ids==set(contexts) and len(removed)==10 and all(r['rule'] in ('AvoidDuplicateLiterals',) for r in original if r['id'] in removed)
    assert len(scope&refs)==2 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8642 and len({r['id'] for r in original}-current)==775 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=13,oldScopeFindings=13,newScopeFindings=3,priorScopeCorrectionsRetained=0,replacedContextWarnings=2,newContextReferencesNet=1,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8652,sourceDerivedRaw=8642,mainRaw=1512,testRaw=7130,totalPriorCorrections=775,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=10,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8642-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
